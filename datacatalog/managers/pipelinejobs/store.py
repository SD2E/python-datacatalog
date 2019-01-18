
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


class ManagedPipelineJob(Manager):
    """Specialized PipelineJob that supports archiving to defined stores and deferred updates

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
        agave (agavepy.agave.Agave, optional): Active TACC.cloud API client
        agent (str, optional): Abaco actorId or Agave appId
        archive_path (str, optional): Override automatic ``archive_path``
        archive_system (str, optional): Override default ``archive_system``
        archive_collection_level (str, optional): Override default of ``measurement`` for aggregating outputs
        data (dict, optional): Arbitrary object describing the job's parameterization
        inputs (list): Data files and refernces being computed upon
        instanced (bool, optional): Whether a ``archive_path`` should be extended with a randomized session name
        pipeline_uuid (str): String UUID5 for the current pipeline
        session (str, optional): A short alphanumeric correlation string
        task (str, optional): Abaco executionId or Agave jobId

    """

    MGR_PARAMS = [
        ('agent', False, 'agent', None),
        ('task', False, 'task', None),
        ('session', False, 'session', interestinganimal.generate(
            timestamp=False)),
        ('data', False, 'data', {}),
        ('level_store', False, 'level_store', 'product'),
        ('archive_path', False, 'archive_path', None),
        ('archive_path_patterns', False, 'archive_path_patterns', []),
        ('archive_collection_level', False, '_archive_collection_level', 'experiment'),
        ('archive_system', False, 'archive_system', DEFAULT_ARCHIVE_SYSTEM)]
    """Keyword parameters for job setup"""

    JOB_PARAMS_ANY_OF = [('pipeline_uuid', True, 'uuid', None, 'pipeline', 'child_of')]
    """Keyword parameters for metadata linkage."""

    COLL_PARAMS = ['experiment_design_id', 'experiment_id', 'sample_id', 'measurement_id']

    def __init__(self, mongodb,
                 pipelines,
                 instanced=True,
                 agave=None,
                 *args,
                 **kwargs):
        super(ManagedPipelineJob, self).__init__(mongodb, agave=agave)
        # self._enforce_auth = True

        # Read in and validate pipeline configuration
        self.config = PipelineJobsConfig(**pipelines)

        # Handle parameters
        for param, required, key, default in self.MGR_PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Manager parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default
            setattr(self, key, kval)

        # Handle collection params. Insert them into data so they can be
        # easily discovered. The actual linkage is done on the UUID for
        # experiment_id if a value for experiment_id was passed to init()
        for param in self.COLL_PARAMS:
            if kwargs.get(param) is not None:
                if param not in self.data:
                    self.data[param] = kwargs.get(param)

        # Init empty linkage arrays
        relations = dict()
        for lf in LINK_FIELDS:
            relations[lf] = list()

        # TODO - This is now just pipeline_uuid. Replace it validation of pipeline_uuid
        for param, required, key, default, store, link in self.JOB_PARAMS_ANY_OF:
            # These chained gets allow config values to come in from
            # init() preferentially with values in PipelineJobsConfig as backup
            kval = kwargs.get(param, self.config.get(param, None))
            if kval is None and required is True:
                raise ManagedPipelineJobError('Job parameter "{}" is required'.format(param))
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

        # Some invocations will have inputs references loaded in their
        # data parameter.
        data_file_uris = self.refs_from_data_dict(self.data, store='files')
        reference_uris = self.refs_from_data_dict(self.data, store='references')

        # print('DATA')
        # pprint(data_file_uris)
        # print('REFERRENCE')
        # pprint(reference_uris)

        data_file_uuids = super(
            ManagedPipelineJob, self).self_from_inputs(data_file_uris)
        reference_uri_uuids = super(
            ManagedPipelineJob, self).self_from_inputs(reference_uris)
        # Read in contents of `inputs` param
        input_file_uuids = super(
            ManagedPipelineJob, self).self_from_inputs(
                kwargs.get('inputs', []))
        # print(input_file_uuids, data_file_uuids, reference_uri_uuids)
        derived_from_uuids = list(
            set(input_file_uuids + data_file_uuids + reference_uri_uuids))

        # print('UUIDS')
        # pprint(derived_from_uuids)

        relations['derived_from'] = derived_from_uuids

        # Set our linkage fields
        for rel, val in relations.items():
            setattr(self, rel, val)

        # sys.exit(1)
        # Attempt to seed archive_path with experiment UUID
        archive_path_els = list()
        lineage_id = None

        if 'archive_path' not in kwargs:
            # The code in here is expensive, so only do it
            # if no archive_path is provided
            try:
                for df_uuid in derived_from_uuids:
                    try:
                        lineage = super(
                            ManagedPipelineJob, self).lineage_from_uuid(df_uuid)
                        lineage_id = super(
                            ManagedPipelineJob, self).level_from_lineage(
                            lineage, self._archive_collection_level)
                        if lineage_id not in archive_path_els:
                            archive_path_els.append(lineage_id)
                    except Exception:
                        pass
            except Exception as exc:
                pprint(exc)

            # Unable to find an experiment upstream of the files
            if len(archive_path_els) == 0:
                try:
                    expt_id = kwargs.get('experiment_id')
                    query = {'experiment_id': expt_id}
                    resp = self.stores['experiment'].find_one_by_id(**query)
                    if resp is not None:
                        if resp.get('uuid', None) is not None:
                            archive_path_els.append(resp.get('uuid'))
                    else:
                        print('Unknown or invalid UUID for experiment_id')
                        # raise ValueError('Unknown or invalid UUID for experiment_id')
                except Exception:
                    raise ManagedPipelineJobError('Unable to resolve experimental metadata lineage from files and/or no valid experiment_id was supplied')

            derived_from_hash = uuid_to_hashid(catalog_uuid(':'.join(self.derived_from), uuid_type='generic'))
            archive_path_els.append(getattr(self, 'pipeline_uuid'))
            archive_path_els.append(derived_from_hash)
            # Build out hashed version of inputs

            setattr(self, '_archive_path_els', archive_path_els)

        self.__canonicalize_agent_and_task()
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
                        'archive_path_patterns': self.archive_path_patterns,
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

    def run(self, data={}):
        """Process a **run** event

        Args: data (dict, optional): Value for job data to store with the event

        Returns:
            object: ``self``
        """
        self.job = self.stores['pipelinejob'].handle({
            'name': 'run',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})
        setattr(self, 'cancelable', False)
        return self.job

    def resource(self, data={}):
        """Process an **resource** event

        Args: data (dict, optional): Value for job data to store with the event

        Returns:
            object: ``self``
        """
        self.job = self.stores['pipelinejob'].handle({
            'name': 'resource',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})

        setattr(self, 'cancelable', False)
        return self.job

    def update(self, data={}):
        """Process an **update** event

        Args: data (dict, optional): Value for job data to store with the event

        Returns:
            object: ``self``
        """
        self.job = self.stores['pipelinejob'].handle({
            'name': 'update',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})

        setattr(self, 'cancelable', False)
        return self.job

    def fail(self, data={}):
        """Process a **fail** event

        Args: data (dict, optional): Value for job data to store with the event

        Returns:
            object: ``self``
        """
        self.job = self.stores['pipelinejob'].handle({
            'name': 'fail',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})
        setattr(self, 'cancelable', False)
        return self.job

    def finish(self, data={}):
        """Process a **finish* event

        Args: data (dict, optional): Value for job data to store with the event

        Returns:
            object: ``self``
        """
        self.job = self.stores['pipelinejob'].handle({
            'name': 'finish',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})
        setattr(self, 'cancelable', False)
        return self.job

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
            self.config['job_indexer_none'],
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
