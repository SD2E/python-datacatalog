
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

DEFAULT_ARCHIVE_SYSTEM = 'data-sd2e-community'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ManagedPipelineJobError(Exception):
    """An error happened in the context of a ManagedPipelineJob"""
    pass

class ManagedPipelineJobInstance(Manager):
    """Supports working with a existing ManagedPipelineJob

    Args:
        mongodb (mongo.Connection): Connection to system MongoDB with write access to ``jobs``
        uuid (str): Job UUID
    """

    # Bring in only minimal set of fields to lift from parent document as
    # the intent of this class is not to update the ManagedPipelineJob but
    # only to take actions that depend on its specific properties
    PARAMS = [
        ('state', False, 'state', None),
        ('archive_path', False, 'archive_path', None),
        ('archive_system', False, 'archive_system', DEFAULT_ARCHIVE_SYSTEM)]

    def __init__(self, mongodb, uuid, agave=None, **kwargs):
        super(ManagedPipelineJobInstance, self).__init__(mongodb, agave)
        self.uuid = uuid
        db_rec = self.stores['pipelinejob'].find_one_by_uuid(uuid)
        for param, req, attr, default in self.PARAMS:
            setattr(self, attr, db_rec.get(param))

    def index_archive_path(self, processing_level="1", filters=[], fixity=False):
        """Discovers and associates files from an archive path with its job

        Args:
            processing_level (str, optional): The "processing level" for indexed files
            filters (list, optional): Set of Python regular expressions to subselect specific files in target path

        Note:
            Regular expressions are concatenated into a single expression at
            run time. This may impact construction of your filter strings. For
            example, ``['sample.tacc.1', 'sample-tacc-1']`` will be evaluated
            as Python regex ``sample.tacc.1|sample-tacc-1``.

        Returns:
            list: Filenames set as ``generated_by`` the specified job
        """
        indexed = list()

        if filters != []:
            patts = re.compile('|'.join(filters))
        else:
            patts = None

        # TODO - Accept other states AFTER finished
        if self.state == 'FINISHED':
            path_listing = self.stores['pipelinejob'].list_job_archive_path(self.uuid, recurse=True, directories=False)
            for file in path_listing:
                if patts is not None:
                    if patts.search(os.path.basename(file)):
                        # When called with this signature, infer_filetype will
                        # always return a FileType object
                        ftype = getattr(infer_filetype(file,
                                                       check_exists=False,
                                                       permissive=True), 'label')
                        frec = FileRecord({'name': file,
                                           'type': ftype,
                                           'level': processing_level})
                        # print('FILEREC', frec)
                        # print('  TYPE', type(frec))
                        resp = FileRecord(self.stores['file'].add_update_document(frec))

                        gen_by = resp.get('generated_by', list())
                        if self.uuid not in gen_by:
                            gen_by.append(self.uuid)
                            resp['generated_by'] = gen_by
                            resp = self.stores['file'].add_update_document(resp)
                        indexed.append((os.path.basename(file), resp['uuid'], resp['type']))

                        try:
                            self.stores['fixity'].index({'name': file})
                        except Exception as exc:
                            logger.warning(
                                'Failed to capture fixity for {}: {}'.format(file, exc))
                # print('INDEXED {}'.format(resp['uuid']))
            return indexed
        else:
            raise ManagedPipelineJobError('Cannot index a job that has not reached FINISHED state')


class ManagedPipelineJob(Manager):
    """Specialized PipelineJob that supports archiving to defined stores and deferred updates

    Args:
        mongodb (mongo.Connection): Connection to system MongoDB with write access to ``jobs``
        manager_id (str): Abaco actorId for ``pipeline-jobs-manager``
        update_nonce (str): Abaco nonce with ``EXECUTE`` entitlement for ``manager_id``

    Keyword Args:
        agent (str, optional): Abaco actorId or Agave appId
        archive_path (str, optional): Override automatic ``archive_path``
        archive_system (str, optional): Override default ``archive_system``
        data (dict, optional): Arbitrary object describing the job's parameterization
        experiment_design_id (str, optional): A valid experiment design ID
        experiment_id (str, optional): A valid **experiment** ID
        instanced (bool, optional): Whether a ``archive_path`` should be extended with a randomized session name
        measurement_id (str, optional): A valid **measurement** ID
        pipeline_uuid (str): String UUID5 for the current pipeline
        sample_id (str): A valid sample ID
        session (str, optional): Short alphanumeric correlation string
        task (str, optional): Abaco executionId or Agave jobId

    Note:
        One of the following must be provided: ``experiment_design_id``, ``experiment_id``, ``sample_id``, ``measurement_id``

    """

    MGR_PARAMS = [
        ('agent', False, 'agent', None),
        ('task', False, 'task', None),
        ('session', False, 'session', None),
        ('data', False, 'data', {}),
        ('level_store', False, 'level_store', 'product'),
        ('archive_path', False, 'archive_path', None),
        ('archive_system', False, 'archive_system', DEFAULT_ARCHIVE_SYSTEM)]
    """Keyword parameters for job setup"""

    JOB_PARAMS_ANY_OF = [('pipeline_uuid', True, 'uuid', None, 'pipeline', 'generated_by')]
    """Keyword parameters for metadata linkage."""

    JOB_PARAMS_ONE_OF = [
        ('sample_id', False, 'sample_id', None, 'sample', 'derived_from'),
        ('experiment_design_id', False, 'experiment_design_id', None, 'experiment_design', 'derived_from'),
        ('experiment_id', False, 'experiment_id', None, 'experiment', 'derived_from'),
        ('measurement_id', False, 'measurement_id', None, 'measurement', 'derived_from')
    ]
    """Keyword parameters for metadata linkage where none are mandatory but one must be provided."""

    def __init__(self, mongodb,
                 manager_id,
                 update_nonce,
                 instanced=True,
                 agave=None,
                 *args,
                 **kwargs):
        super(ManagedPipelineJob, self).__init__(mongodb, agave)
        # self._enforce_auth = True
        self.manager = manager_id
        self.nonce = update_nonce
        self.cancelable = True

        self.agent = None
        self.archive_path = None
        self.archive_system = None
        self.data = None
        self.task = None
        self.pipeline_uuid = None
        self.session = None
        self.uuid = None

        for param, required, key, default in self.MGR_PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Manager parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default
            setattr(self, key, kval)

        relations = dict()
        for lf in LINK_FIELDS:
            relations[lf] = list()

        for param, required, key, default, store, link in self.JOB_PARAMS_ANY_OF:
            kval = kwargs.get(param, None)
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
        for rel, val in relations.items():
            setattr(self, rel, val)

        count_one_of_params = 0
        for param, required, key, default, store, link in self.JOB_PARAMS_ONE_OF:
            kval = kwargs.get(param, None)
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
                    count_one_of_params = count_one_of_params + 1
        for rel, val in relations.items():
            setattr(self, rel, val)
        if count_one_of_params == 0:
            raise ManagedPipelineJobError(
                'One of the following job parameters must be provided: {}'.format(
                    [p[0] for p in self.JOB_PARAMS_ONE_OF]))

        self.__canonicalize_agent_and_task()
        self.__set_archive_path(instanced, *args, **kwargs)

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

    def __canonicalize_system(self, system_id):
        api = getattr(self, 'api_server')
        return api + '/systems/v2/' + system_id

    def canonicalize_job(self, job_id):
        api = getattr(self, 'api_server')
        return api + '/jobs/v2/' + job_id

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

    def __set_archive_path(self, instanced=True, level_store='product', *args, **kwargs):

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
        FIELDS = ('experiment_design_id', 'experiment_id', 'sample_id', 'measurement_id', 'pipeline_uuid')
        """Identity and order of document keys used to construct archive_path"""

        path_elements = ['/', 'products', 'v2']
        for field in FIELDS:
            if field in kwargs:
                # TODO: Implement a shorter hash than UUID5 in identifiers.typeduuid and use for path construction
                path_elements.append(getattr(self, field))
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

    def build_webhook(self):
        """Build a webhook for updating this job via callback

        Sending **event** messages over HTTP POST to this webhook will result
        in the ``pipeline-jobs-manager`` Reactor making managed updates to this
        job's state.

        Returns:
            str: A callback URL
        """

        uri = '{}/actors/v2/{}/messages?x-nonce={}&token={}&uuid={}'.format(
            self.api_server, self.manager, self.nonce, self.token, self.uuid)
        # Sanity check - was a valid URL assembled?
        validators.url(uri)
        return uri
