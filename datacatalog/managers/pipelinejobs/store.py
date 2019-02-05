
import arrow
import copy
import json
import os
import re
import sys
import validators
import logging
from pprint import pprint
from ... import identifiers
from .jobmanager import JobManager, data_merge
from ...tokens import get_token
from ...linkedstores.pipelinejob import DEFAULT_LINK_FIELDS as LINK_FIELDS
from ...linkedstores.basestore import formatChecker
from ...linkedstores.file import FileRecord, infer_filetype
from ...identifiers.typeduuid import catalog_uuid, uuid_to_hashid
from .config import PipelineJobsConfig, DEFAULT_ARCHIVE_SYSTEM
from .exceptions import ManagedPipelineJobError
from ...identifiers import interestinganimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# automated-process
DEFAULT_PROCESS_ID = '1176bd3e-8666-547b-bc36-25a3b62fc271'
# measurement.tacc.0x00000000
DEFAULT_MEASUREMENT_ID = '10452d7e-7f0a-59df-a1a3-c5bb44e07f2f'

class ManagedPipelineJob(JobManager):
    """Specialized PipelineJob that supports archiving to defined stores and deferred updates

    1. ``uuid`` is assigned as hash of ``pipeline_uuid`` and ``data`` during ``setup()``
    2. ``archive_path`` is either specified in ``init()`` or generated from XXXX. The latter is the default behavior and is considered SD2 project best practice.
    3. When ``archive_path`` is generated, it is "instanced" by default. This means the root of generated path will be predictable, but will include a terminal directory **adjective-animal-date** for collision avoidance. Pass ``instanced=False`` to disable this behavior.
    4. A job's linkages enable discoverability of its outputs relative to the primary experimental metadata. Consequently, they are very carefully specified. A job is ``generated_by`` one computational **pipeline** and is a ``child_of`` one or more **measurements**.
    5. The file contents of ``archive_path`` are directly associated with the job via a ``generated_by`` relationship after job runs to completion

    The ``child_of`` relationship is established when the job is initialized by
    looking in ``kwargs`` for and resolving into a list of measurements:
    (``measurement_id``, ``sample_id``, then ``experiment_id``). These can be
    passed either as single strings or as a list of strings. Either canonical
    identifiers (``measurement_id``, ``sample_id``, and ``experiment_id`` values)
    or their corresponding UUID5 values can be used. At least one of
    (experiment_id, sample_id, measurement_id) must be passed to ``init()``
    to connect a job to its upstream metadata.

    The job's ``archive_path`` is generated as follows (if ``archive_path`` is
    not specified at ``init()``): It begins with a prefix `/products/v2`, to
    which is added a representation of the **pipeline**. Next, the contents of
    the job's ``data`` slot (which contains parameterization details) are hashed
    and added to the path. Finally, depending on whether ``measurement_id``,
    ``sample_id``, or ``experiment_id`` were passed, the primary identifiers at
    that level of the metadata hieararchy are hashed to produce a distinct
    signature, which is appended to the path. The net result is that each
    combination of pipeline, parameterization, and metadata linkages is
    stored in a unique, collision-proof storage location.

    Args:
        mongodb (mongo.Connection): Connection to system MongoDB with write access to ``jobs``
        pipelines (dict/PipelineJobsConfig): Pipelines configuration

    Keyword Args:
        experiment_id (str/list, optional): Identifier(s) for the experiment(s) to which the job is linked
        sample_id (str/list, optional): Identifer(s) for the sample(s) to which the job is linked
        measurement_id (str/list, optional): Identifier(s) for the measurement(s) to which the job is linked
        data (dict, optional): Defines the job's parameterization.
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
        At least one of (experiment_id, sample_id, measurement_id) must be passed to ``init()`` to explicitly connect a job to upstream experimental metadata.
    """

    PARAMS = [
        ('agent', False, 'agent', None),
        ('task', False, 'task', None),
        ('session', False, 'session', None),
        ('data', False, 'data', {}),
        ('level_store', False, 'level_store', 'product'),
        ('archive_path', False, 'archive_path', None),
        ('archive_patterns', False, 'archive_patterns', []),
        # ('archive_collection_level', False, '_archive_collection_level', 'experiment'),
        ('archive_system', False, 'archive_system', DEFAULT_ARCHIVE_SYSTEM),
        ('uuid', False, 'uuid', None)]
    """Keyword parameters for job setup"""

    INIT_LINK_PARAMS = [('pipeline_uuid', True, 'uuid', None, 'pipeline', 'child_of')]
    """Keyword parameters for metadata linkage."""

    COLL_PARAMS = [('measurement_id', 'measurement'),
                   ('sample_id', 'sample'),
                   ('experiment_id', 'experiment')]

    def __init__(self, mongodb,
                 pipelines,
                 instanced=False,
                 agave=None,
                 *args,
                 **kwargs):
        super(ManagedPipelineJob, self).__init__(mongodb, agave=agave)

        # Read in additional kwargs as per PARAMS
        for param, required, key, default in self.PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default
            setattr(self, key, kval)

        # Validate passed token
        setattr(self, '_enforce_auth', True)

        # agent and task if not provided
        # TODO - lookup should be established in settings module
        if self.agent is None:
            setattr(self, 'agent', os.environ.get('_abaco_actor_id', None))
        if self.task is None:
            setattr(self, 'task', os.environ.get('_abaco_execution_id', None))
        self.__canonicalize_agent_and_task()

        # We're going to create and manage
        # a job so start out as cancelable
        self.cancelable = True

        # Validate pipeline configuration
        self.config = PipelineJobsConfig(**pipelines)

        # Create a session name if not provided
        if self.session is None:
            setattr(self, 'session', interestinganimal.generate(
                timestamp=False))

        # Build archive_path and linkages from job parameterization
        archive_path_els = list()
        relations = dict()
        for lf in LINK_FIELDS:
            relations[lf] = list()

        # Establish **generated_by** linkage
        #
        # Here, we look first to pipeline_uuid parameter, then to contents
        # of pipeline configuration passed in to init()
        GEN_BY_CFG = [(
            'pipeline_uuid', True, 'uuid', None, 'pipeline', 'generated_by')]
        for param, req, key, default, store, link in GEN_BY_CFG:
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

        # Establish **child_of**
        #
        # Connect with experiment/sample/measurement
        archive_path_metadata_els = None
        # Experiment metadata association
        child_of_list = list()
        try:
            # If measurements are passed, use them for linkage and
            meas_provided = False
            if kwargs.get('measurement_id', None) is not None:
                child_of_list = self.measurements_from_measurements(kwargs.get('measurement_id'))
                archive_path_metadata_els = copy.copy(child_of_list)
                meas_provided = True
            if kwargs.get('sample_id', None) is not None:
                if meas_provided is False:
                    child_of_list = self.measurements_from_samples(kwargs.get('sample_id'))
                archive_path_metadata_els = self.samples_from_samples(
                    kwargs.get('sample_id'))
            elif kwargs.get('experiment_id', None) is not None:
                if meas_provided is False:
                    child_of_list = self.measurements_from_experiments(kwargs.get('experiment_id'))
                archive_path_metadata_els = self.experiments_from_experiments(
                    kwargs.get('experiment_id'))
            if not len(child_of_list) > 0:
                raise ValueError("Failed to link job to measurements")
            if not len(archive_path_metadata_els) > 0:
                raise ValueError("Failed to identify metadata elements for archive path")
        except ValueError:
            child_of_list = [DEFAULT_MEASUREMENT_ID]
            archive_path_metadata_els = copy.copy(child_of_list)
        # Set the actual linkage to measurements
        relations['child_of'] = child_of_list

        # Serialize and hash measurement(s), then add to path elements list
        archive_path_els.append(
            uuid_to_hashid(
                catalog_uuid(':'.join(
                    archive_path_metadata_els), uuid_type='generic')))

        # Serialize self.data, generate a hash, add to archive_path_els
        archive_path_els.append(
            uuid_to_hashid(
                catalog_uuid(
                    self.serialize_data(), uuid_type='generic')))

        # Establish linkages to named, managed files and references
        #
        # Resolve managed files from 'inputs' to UUIDs The working
        # assumption is that only agave-canonical URI will be present
        input_file_uuids = super(
            ManagedPipelineJob, self).self_from_inputs(
                kwargs.get('inputs', []))

        # Identify and resolve to typed UUIDs the URIs of managed
        # files and references in self.inputs and self.data
        data_file_uris = self.refs_from_data_dict(self.data, store='files')
        data_file_uuids = super(
            ManagedPipelineJob, self).self_from_inputs(data_file_uris)
        # Reduce to the non-redudant set of file UUIDs
        acts_on_uuids = list(
            set(input_file_uuids + data_file_uuids))

        # References
        reference_uris = self.refs_from_data_dict(self.data, store='references')
        reference_uri_uuids = super(ManagedPipelineJob,
                                    self).self_from_inputs(reference_uris)

        # Store values in appropriate slot in "relations"
        relations['acts_on'].extend(acts_on_uuids)
        relations['acts_using'].extend(reference_uri_uuids)

        # Finally, set this document's linkage attributes
        for rel, val in relations.items():
            setattr(self, rel, val)

        # Compute the archive path
        # /products/v2/pipeline_uuid/hash(child_of)/hash(data)

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
        # TODO - I do not like recapitulating the schema here. Solve somehow
        job_document = {'pipeline_uuid': self.pipeline_uuid,
                        'archive_path': self.archive_path,
                        'archive_patterns': self.archive_patterns,
                        'archive_system': self.archive_system,
                        'data': self.data,
                        'session': self.session,
                        'agent': self.agent,
                        'task': self.task,
                        'generated_by': self.generated_by,
                        'child_of': self.child_of,
#                        'derived_from': self.derived_from,
                        'acts_on': self.acts_on,
                        'acts_using': self.acts_using
                        }

        # Retrieves reference to existing job if exists
        job_uuid = self.stores['pipelinejob'].uuid_from_properties(job_document)
        new_job = self.stores['pipelinejob'].find_one_by_uuid(job_uuid)
        if new_job is None:
            new_job = self.stores['pipelinejob'].create(job_document)
        token = get_token(new_job['_salt'], self.stores['pipelinejob'].get_token_fields(new_job))

        setattr(self, 'uuid', new_job['uuid'])
        setattr(self, 'job', new_job)
        setattr(self, 'token', token)
        self.set_callbacks()
        return self

    def set_callbacks(self):
        """Establish the web service callbacks for the job
        """
        setattr(self, 'callback', self.build_webhook())
        setattr(self, 'indexer_callback', self.build_indexer_webhook())
        return self

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

    def __repr__(self):
        reprvals = list()
        for param in ['uuid', 'pipeline_uuid', 'data', 'child_of', 'generated_by', 'acts_on', 'acts_using']:
            val = getattr(self, param, None)
            if isinstance(val, list):
                val = str(val)
            reprvals.append('{} : {}'.format(param, val))
        reprvals.append('archive_uri: ' + self.archive_uri())
        return '\n'.join(reprvals)

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
        """Sets the document's archive_path
        """
        if 'archive_path' in kwargs:
            ap = kwargs.get('archive_path')
        else:
            ap = self.get_archive_path(instanced, *args, **kwargs)
        setattr(self, 'archive_path', ap)
        return self

    def get_archive_path(self, instanced=True, *args, **kwargs):
        """Computes and returns the document's archive_path
        """
        path_elements = ['/', 'products', 'v2']
        path_elements.extend(getattr(self, '_archive_path_els', []))
        archive_path = os.path.join(*path_elements)
        # Compress path by removing any UUID dash characters
        archive_path = archive_path.replace('-', '')
        if instanced is True:
            archive_path = os.path.join(
                archive_path, self.instanced_directory(
                    getattr(self, 'session')))

        return archive_path

    # def serialize_data(self):
    #     """Serializes self.data into a minified string
    #     """
    #     return json.dumps(getattr(self, 'data', {}),
    #                       sort_keys=True,
    #                       separators=(',', ':'))

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
