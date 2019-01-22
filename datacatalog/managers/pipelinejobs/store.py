
import arrow
import os
import re
import sys
import validators
import logging
from pprint import pprint
from ... import identifiers
from ..common import Manager, data_merge
from ...tokens import get_token
from ...linkedstores.basestore import DEFAULT_LINK_FIELDS as LINK_FIELDS
from ...linkedstores.basestore import formatChecker
from ...linkedstores.file import FileRecord, infer_filetype
from ...identifiers.typeduuid import catalog_uuid, uuid_to_hashid
from .config import PipelineJobsConfig, DEFAULT_ARCHIVE_SYSTEM
from .exceptions import ManagedPipelineJobError
from ...identifiers import interestinganimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# automated-process
DEFAULT_JOB_GENERATED_BY = '1176bd3e-8666-547b-bc36-25a3b62fc271'

class ManagedPipelineJob(Manager):
    """Specialized PipelineJob that supports archiving to defined stores and deferred updates

    1. ``uuid`` is assigned as hash of ``pipeline_uuid`` and ``data`` during ``setup()``
    2. ``archive_path`` is either specified in ``init()`` or generated from XXXX. The latter is the default behavior and is considered SD2 project best practice.
    3. When ``archive_path`` is generated, it is instanced by default. This means the root of generated path will be predictable, but will include a terminal directory named **adjective-animal-date**. Pass ``instanced=False`` to disable this behavior.
    4. A jobs' linkages enable discoverability of job outputs with respect to primary experimental metadata. Consequently, they are very carefully specified. A job is the ``child_of`` one specific computational ``pipeline`, ``derived_from`` the experiment/sample/measurement that provided its inputs as well as the specific inputs and references themselves, and are ``generated_by`` a named ``process`` (default: **automated-process**).
    5. A job is only able to assert metadata linkage to its ``archive_path``  directory. The contents of ``archive_path`` are associated with the job via an **indexer** process that runs when the job is complete. The result is that the contents of ``archive_path` are set to be ``generated_by`` a specific job.

    The default ``archive_path`` is set based on the compute pipeline plus the
    complete parental lineage of the job's inputs. This can be overridden by
    providing a ``archive_collection_level`` of **sample**, **experiment**, or
    **experiment_design**. If that level is uniquely resolvable in the
    parental lineage, that will be the level at which job outputs are
    collected. It is also possible (to accomodate special cases), to manually
    specify ``archive_path``.

    The job's ``derived_from`` linkage is set to the distinct contents of
    ``datafiles`` and ``otherfiles``. Its ``child_of`` linkage is set to
    the job's pipeline. No support for setting ``generated_by`` is
    available. These linkages are mandatory and there presently no plan to
    enable user overrides.

    Args:
        mongodb (mongo.Connection): Connection to system MongoDB with write access to ``jobs``
        pipelines (dict/PipelineJobsConfig): Pipelines configuration

    Keyword Args:
        experiment_id (str, optional): Identifier for the experiment from which the job is derived
        sample_id (str, optional): Identifer for sample at which the job outputs should be collected. Must validate as a child of ``experiment_id``.
        measurement_id (str, optional): Identifer for measurement at which the job outputs should be collected. Must validate as a child of ``sample_id``.
        data (dict, optional): Dictionary object describing the job's parameterization. Provides the basis for the job's ``.data`` field.
        archive_path (str, optional): Override value for automatically-generated ``archive_path``
        archive_patterns (list, optional): List of strings in Python regex format used to select contents of ``archive_path`` for association with the job
        instanced (bool, optional): Should ``archive_path`` be extended with a randomized session name
        session (str, optional): A short alphanumeric correlation string
        agave (agavepy.agave.Agave, optional): Active TACC.cloud API client. Needed only to resolve references to Agave or Abaco entities.

    Other Parameters:
        agent (str, optional): Abaco actorId or Agave appId managing the pipeline
        archive_collection_level (str, optional): Overrides default of ``measurement`` for aggregating outputs
        archive_system (str, optional): Overrides default ``archive_system``
        inputs (list, optional): Data files and references being computed upon. This supplements values of ``inputs`` discovered in ``data``
        generated_by: (str, optional): String UUID5 of a named process
        pipeline_uuid (str, optional): Overrides value of ``pipelines.pipeline_uuid``
        task (str, optional): The specific instance of agent

    Note:
        At least one of (experiment_id, sample_id, measurement_id) must be passed to ``init()`` to explicitly connect a job to upstream experimental metadata. The linkages may still be inferred without it, as the job will be associated with specific input files, but that can be tricky if there are jobs that re-use or share some files.
    """

    MGR_PARAMS = [
        ('agent', False, 'agent', None),
        ('task', False, 'task', None),
        ('session', False, 'session', None),
        ('data', False, 'data', {}),
        ('level_store', False, 'level_store', 'product'),
        ('archive_path', False, 'archive_path', None),
        ('archive_patterns', False, 'archive_patterns', []),
        # ('archive_collection_level', False, '_archive_collection_level', 'experiment'),
        ('archive_system', False, 'archive_system', DEFAULT_ARCHIVE_SYSTEM)]
    """Keyword parameters for job setup"""

    INIT_LINK_PARAMS = [('pipeline_uuid', True, 'uuid', None, 'pipeline', 'child_of')]
    """Keyword parameters for metadata linkage."""

    COLL_PARAMS = [('measurement_id', 'measurement', 'derived_from'),
                   ('sample_id', 'sample', 'derived_from'),
                   ('experiment_id', 'experiment', 'derived_from')]

    def __init__(self, mongodb,
                 pipelines,
                 instanced=True,
                 agave=None,
                 *args,
                 **kwargs):
        super(ManagedPipelineJob, self).__init__(mongodb, agave=agave)
        # self._enforce_auth = True

        # Initialize empty linkage arrays
        relations = dict()
        for lf in LINK_FIELDS:
            relations[lf] = list()

        # List of elements that can be used to synthesize archive_path
        archive_path_els = list()

        # Validate pipeline configuration
        self.config = PipelineJobsConfig(**pipelines)
        self.cancelable = True

        # Handle manager parameters
        for param, required, key, default in self.MGR_PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default
            setattr(self, key, kval)

        # Create a session name if not provided
        if self.session is None:
            setattr(self, 'session', interestinganimal.generate(
                timestamp=False))

        # Inspect os.environ to assign agent and task if not provided
        # TODO - these should be established in settings module
        if self.agent is None:
            setattr(self, 'agent', os.environ.get('_abaco_actor_id', None))
        if self.task is None:
            setattr(self, 'task', os.environ.get('_abaco_execution_id', None))
        self.__canonicalize_agent_and_task()

        # Establish **child_of** linkage
        #
        # Here, we look first to pipeline_uuid parameter, then to contents
        # of pipeline configuration passed in to init()
        CHILD_OF_CFG = [(
            'pipeline_uuid', True, 'uuid', None, 'pipeline', 'child_of')]
        for param, req, key, default, store, link in CHILD_OF_CFG:
                kval = kwargs.get(param, self.config.get(param, None))
                if kval is None and req is True:
                    raise ManagedPipelineJobError('Parameter "{}" is required'.format(param))
                else:
                    if kval is None:
                        kval = default
                if kval is not None:
                    # Validates each job param against catalog
                    resp = self.__get_stored_doc(store, key, kval)
                    if resp is None:
                        raise ManagedPipelineJobError(
                            'Failed to verify {}:{} exists in store {}'.format(
                                param, kval, store))
                    else:
                        uuidval = resp.get('uuid')
                        setattr(self, param, uuidval)
                        relations[link].append(uuidval)
        archive_path_els.append(getattr(self, 'pipeline_uuid'))

        # Establish **generated_by**
        # TODO - allow this to be passed to init()
        if 'generated_by' in kwargs:
            pass
        else:
            relations['generated_by'] = [DEFAULT_JOB_GENERATED_BY]

        # Establish **derived_from**
        #
        # Connect with experiment/sample/measurement

        # Handle collection-level parameters
        #
        # Insert the human-readable IDs into job.data so they can be
        # easily read and searched on. Actual linkage is done on their UUID
        #
        # While we are doing this, also populate archive_path_els
        for param, coll, rel in self.COLL_PARAMS:
            val = kwargs.get(param)
            if val is not None:
                q = {param: val}
                resp = self.stores[coll].find_one_by_id(**q)
                if resp is not None:
                    if param not in self.data:
                        self.data[param] = kwargs.get(param)
                    val_uuid = resp.get('uuid')
                    relations['derived_from'].append(val_uuid)
                    archive_path_els.append(val_uuid)
                    # Stop at the first collection level that was passed
                    # break
                else:
                    raise ValueError(
                        'Unknown value for {}: {}'.format(coll, val))

        # Extend **derived_from** with any resolvable references to managed
        # files or references
        #
        # 1. Resolve contents of inputs parameter to UUIDs. The working
        # assumption is that only agave-canonical URI will be present
        input_file_uuids = super(
            ManagedPipelineJob, self).self_from_inputs(
                kwargs.get('inputs', []))

        # 2. Intelligently identify and resolve to UUIDs the URIs of managed
        # files and references in self.inputs and self.data
        data_file_uris = self.refs_from_data_dict(self.data, store='files')
        data_file_uuids = super(
            ManagedPipelineJob, self).self_from_inputs(data_file_uris)
        reference_uris = self.refs_from_data_dict(self.data, store='references')
        reference_uri_uuids = super(ManagedPipelineJob,
                                    self).self_from_inputs(reference_uris)

        # 3. Reduce to the non-redudant set of UUIDs
        # The job is derived from these for the purposes of metadata inheritance
        derived_from_uuids = list(
            set(input_file_uuids + data_file_uuids + reference_uri_uuids))
        # This is already populated by the link to experiment, sample, meas
        # and this is why we extend rather than just set via =
        relations['derived_from'].extend(derived_from_uuids)

        # Set the document's linkage attributes
        for rel, val in relations.items():
            setattr(self, rel, val)


        # lineage_id = None
        # if 'archive_path' not in kwargs:
        #     # The code in here is expensive, so only do it
        #     # if no archive_path is provided
        #     try:
        #         for df_uuid in derived_from_uuids:
        #             try:
        #                 lineage = super(
        #                     ManagedPipelineJob, self).lineage_from_uuid(df_uuid)
        #                 lineage_id = super(
        #                     ManagedPipelineJob, self).level_from_lineage(
        #                     lineage, self._archive_collection_level)
        #                 if lineage_id not in archive_path_els:
        #                     archive_path_els.append(lineage_id)
        #             except Exception:
        #                 pass
        #     except Exception as exc:
        #         pprint(exc)

            # # Unable to find an experiment upstream of the files
            # if len(archive_path_els) == 0:
            #     try:
            #         expt_id = kwargs.get('experiment_id')
            #         query = {'experiment_id': expt_id}
            #         resp = self.stores['experiment'].find_one_by_id(**query)
            #         if resp is not None:
            #             if resp.get('uuid', None) is not None:
            #                 archive_path_els.append(resp.get('uuid'))
            #         else:
            #             print('Unknown or invalid UUID for experiment_id')
            #             # raise ValueError('Unknown or invalid UUID for experiment_id')
            #     except Exception:
            #         raise ManagedPipelineJobError('Unable to resolve experimental metadata lineage from files and/or no valid experiment_id was supplied')

        # Build archive path
        # /products/v2/<derivations>/pipeline_uuid
        # derived_from_hash = uuid_to_hashid(catalog_uuid(':'.join(self.derived_from), uuid_type='generic'))
        # archive_path_els.append(derived_from_hash)
        # Build out hashed version of inputs
        setattr(self, '_archive_path_els', archive_path_els)
        self.set_archive_path(instanced, *args, **kwargs)

    def setup(self, data={}):
        """Finish initializing the manager

        Args: data (dict, optional): Override or set value for job data

        Returns:
            object: ``self``
        """
        init_data = getattr(self, 'data', dict())
        setup_data = data_merge(init_data, data)
        setattr(self, 'data', setup_data)
        job_document = {'pipeline_uuid': self.pipeline_uuid,
                        'archive_path': self.archive_path,
                        'archive_patterns': self.archive_patterns,
                        'archive_system': self.archive_system,
                        'data': self.data,
                        'session': self.session,
                        'agent': self.agent,
                        'task': self.task,
                        'child_of': self.child_of,
                        'derived_from': self.derived_from,
                        'generated_by': self.generated_by
                        }
        new_job = self.stores['pipelinejob'].create(job_document)
        token = get_token(new_job['_salt'], self.stores['pipelinejob'].get_token_fields(new_job))

        setattr(self, 'uuid', new_job['uuid'])
        setattr(self, 'job', new_job)
        setattr(self, 'token', token)
        setattr(self, 'callback', self.build_webhook())
        setattr(self, 'indexer_callback', self.build_indexer_webhook())
        # raise Exception(self.job)
        return self

    def handle(self, event_name, data={}):
        """Handle a named event
        """
        self.job = self.stores['pipelinejob'].handle({
            'name': event_name.lower(),
            'uuid': self.uuid,
            'token': self.token,
            'data': data})
        if getattr(self, 'cancelable'):
            setattr(self, 'cancelable', False)
        return self.job

    def run(self, data={}):
        """Wrapper for **run**
        """
        return self.handle('run', data)

    def resource(self, data={}):
        """Wrapper for **resource**
        """
        return self.handle('resource', data)

    def update(self, data={}):
        """Wrapper for **update**
        """
        return self.handle('update', data)

    def fail(self, data={}):
        """Wrapper for **fail**
        """
        return self.handle('fail', data)

    def finish(self, data={}):
        """Wrapper for **finish**
        """
        return self.handle('finish', data)

    def index(self, data={}):
        """Wrapper for **index**
        """
        return self.handle('index', data)

    def indexed(self, data={}):
        """Wrapper for **indexed**
        """
        return self.handle('indexed', data)

    def cancel(self):
        """Cancel the job, deleting it from the system
        """
        if getattr(self, 'cancelable') is not False:
            self.stores['pipelinejob'].delete(self.uuid, self.token, soft=False)
            self.job = None
            return self.job
        else:
            raise ManagedPipelineJobError(
                'Cannot cancel a job once it is running. Send a "fail" event instead.')

    def build_webhook(self):
        """Return a webhook to update this job via web callback

        Sending **event** messages over HTTP POST to this webhook will result
        in the ``pipelinejobs-manager`` Reactor making managed updates to this
        job's state.

        Returns:
            str: A callback URL
        """

        uri = '{}/actors/v2/{}/messages?x-nonce={}&token={}&uuid={}'.format(
            self.api_server, self.config['job_manager_id'],
            self.config['job_manager_nonce'],
            self.token, self.uuid)
        # Sanity check - was a valid URL assembled?
        validators.url(uri)
        return uri

    def build_indexer_webhook(self):
        """Return a webhook to index job outputs via web callback

        Sending a *index* message to this webhook will index the job output

        Returns:
            str: A callback URL
        """

        uri = '{}/actors/v2/{}/messages?x-nonce={}&token={}&uuid={}'.format(
            self.api_server, self.config['job_indexer_id'],
            self.config['job_indexer_nonce'],
            self.token, self.uuid)
        # Sanity check - was a valid URL assembled?
        validators.url(uri)
        return uri

    def __canonicalize_agent_and_task(self):
        """Extend simple text ``agent`` and ``task`` into REST URIs
        """
        oagent = getattr(self, 'agent', None)
        otask = getattr(self, 'task', None)

        if oagent is not None:
            # Agave appID
            if identifiers.agave.appid.validate(oagent, permissive=True):
                agent = self.canonicalize_app(oagent)
            else:
                # TODO: Validate abaco actorid
                agent = self.canonicalize_actor(oagent)
            setattr(self, 'agent', agent)

        if otask is not None:
            # TODO: Replace with identifiers.agave.uuids.validate('job', task)
            if otask.endswith('-007'):
                task = self.canonicalize_app(otask)
            else:
                # TODO: Validate abaco execid
                task = self.canonicalize_execution(oagent, otask)
            setattr(self, 'task', task)

        return self

    def canonicalize_actor(self, actor_id):
        api = getattr(self, 'api_server')
        return api + '/actors/v2/' + actor_id

    def canonicalize_execution(self, actor_id, exec_id):
        resp = self.canonicalize_actor(actor_id) + '/executions/' + exec_id
        return resp

    def canonicalize_app(self, app_id):
        api = getattr(self, 'api_server')
        return api + '/apps/v2/' + app_id

    def canonicalize_system(self, system_id):
        api = getattr(self, 'api_server')
        return api + '/systems/v2/' + system_id

    def canonicalize_job(self, job_id):
        api = getattr(self, 'api_server')
        return api + '/jobs/v2/' + job_id

    def set_archive_path(self, instanced=True, level_store='product', *args, **kwargs):

        if 'archive_path' in kwargs:
            ap = kwargs.get('archive_path')
        else:
            ap = self.get_archive_path(instanced, level_store, *args, **kwargs)
        setattr(self, 'archive_path', ap)
        return self

    def get_archive_path(self, instanced=True, level_store='product',
                         session=None, path=None, *args, **kwargs):

        # Allow user to pass `path at init time to create a custom archive_path`
        if path is not None:
            if not path.startswith('/'):
                raise ValueError('The override value passed for "path" must be an absolute path')

            return path

        if level_store == 'product':
            ap = self.__archive_path_for_product(instanced, session, *args, **kwargs)

        return ap

    def __compress_path(self, in_path):
        # Compress a path by removing the dashes, which arise from
        # using UUID5 as path elements.
        return in_path.replace('-', '')

    def __archive_path_for_product(self, instanced=True, session=None, *args, **kwargs):

        path_elements = ['/', 'products', 'v2']
        path_elements.extend(getattr(self, '_archive_path_els', []))
        product_path = os.path.join(*path_elements)
        product_path = self.__compress_path(product_path)
        if instanced is True:
            product_path = os.path.join(product_path, self.instanced_directory(session))

        return product_path

    def __archive_path_for_reference(self, *args, **kwargs):
        raise NotImplementedError()

        FIELDS = ()
        path_elements = ['/', 'references']
        for field in FIELDS:
            if field in kwargs:
                path_elements.append(getattr(self, field))
        # raise Exception(path_elements)
        return os.path.join(*path_elements)

    def __archive_path_for_upload(self, *args, **kwargs):
        raise NotImplementedError()

        FIELDS = ()
        path_elements = ['/', 'uploads']
        for field in FIELDS:
            if field in kwargs:
                path_elements.append(getattr(self, field))
        # raise Exception(path_elements)
        return os.path.join(*path_elements)

    def instanced_directory(self, session=None):
        """Extend a path with an instanced directory name

        Args:
            session (str, optional): Short alphanumeric session string

        Returns:
            str: The new instance directory name
        """
        if session is None or len(session) < 4:
            return identifiers.interestinganimal.generate()
        if not session.endswith('-'):
            session = session + '-'
        return session + arrow.utcnow().format('YYYYMMDDTHHmmss') + 'Z'

    def __get_stored_doc(self, store, key, val):
        return self.stores[store].coll.find_one({key: val})

    def refs_from_data_dict(self, data={}, store='files'):
        """Find agave-canonical URI from data dicts

        Discover late-bound links to files and references from the contents
        of ``inputs`` and ``parameters`` keys in a ``data`` dictionary.

        Args:
            data (dict): A data dictionary
            store (string, optional): Which store to resolve against (files|references)

        Returns:
            list: Discovered list of managed file- or reference URIs
        """

        refs = list()
        if store == 'files':
            patterns = {'URI': re.compile('(^agave:\/\/([a-z0-9-A-Z_-])+)?/(uploads|products)/'),
                        'FileStore': re.compile('/uploads/|/products/')}
        elif store == 'references':
            patterns = {'URI': re.compile('(^agave:\/\/([a-z0-9-A-Z_-])+)?/reference/|^(http:|https:)'),
                        'FileStore': re.compile('/reference/')}
        else:
            raise ValueError('{} is not a valid value for parameter "store"'.format(store))

        # Process dict or list form of 'inputs'
        inputs = data.get('inputs', None)
        # Agave case
        if isinstance(inputs, dict):
            for iname in list(inputs.keys()):
                fname = inputs[iname]
                if not patterns['URI'].search(fname):
                    # TODO - pick up default from global config
                    fname = 'agave://data-sd2e-community' + fname
                if fname not in refs:
                    refs.append(fname)
        elif isinstance(inputs, list):
            for fname in inputs:
                if patterns['URI'].search(fname):
                    if fname not in refs:
                        refs.append(fname)

        # Process parameters dict
        params = data.get('parameters', None)
        if isinstance(params, dict):
            for pname in list(params.keys()):
                fname = params[pname]
                # Grab all agave:// references
                if patterns['URI'].search(fname) and fname not in refs:
                    refs.append(fname)
                    continue
                elif patterns['FileStore'].search(fname):
                    fname = 'agave://data-sd2e-community' + fname
                    if fname not in refs:
                        refs.append(fname)
                    continue

        return refs
