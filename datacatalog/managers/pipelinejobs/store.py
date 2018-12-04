
import os
import sys
import validators
from pprint import pprint
from ... import identifiers
from ..common import Manager
from ...tokens import get_token
from ...linkedstores.basestore import DEFAULT_LINK_FIELDS as LINK_FIELDS

class ManagedPipelineJobError(Exception):
    """An error happened in the context of a ManagedPipelineJob"""
    pass

class ManagedPipelineJob(Manager):
    """Specialized PipelineJob that supports archiving to defined stores and deferred updates

    Args:
        mongodb (mongo.Connection): Connection to system MongoDB with write access to ``jobs``
        manager_id (str): Abaco actorId for ``pipeline-jobs-manager``
        update_nonce (str): Abaco nonce with ``EXECUTE`` entitlement for ``manager_id``

    Keyword Args:
        agent (str, optional): Abaco actorId or Agave appId
        data (dict, optional): Arbitrary object describing the job's parameterization
        experiment_design_id (str, optional): A valid experiment design ID
        experiment_id (str, optional): A valid **experiment** ID
        measurement_id (str, optional): A valid **measurement** ID
        pipeline_uuid (str): String UUID5 for the current pipeline
        sample_id (str): A valid sample ID
        session (str, optional): Short alphanumeric correlation string
        task (str, optional): Abaco executionId or Agave jobId

    """

    MGR_PARAMS = [
        ('agent', False, 'actor_id', None),
        ('task', False, 'task', None),
        ('session', False, 'session', None),
        ('data', False, 'data', {}),
        ('level_store', False, 'level_store', 'product')]
    """Keyword parameters for job setup"""

    JOB_PARAMS = [
        ('pipeline_uuid', True, 'uuid', None, 'pipeline', 'generated_by'),
        ('sample_id', True, 'sample_id', None, 'sample', 'derived_from'),
        ('experiment_design_id', False, 'experiment_design_id', None, 'experiment_design', 'derived_from'),
        ('experiment_id', False, 'experiment_id', None, 'experiment', 'derived_from'),
        ('measurement_id', False, 'measurement_id', None, 'measurement', 'derived_from'),
    ]
    """Keyword parameters for metadata linkage"""

    def __init__(self, mongodb,
                 manager_id,
                 update_nonce,
                 *args,
                 **kwargs):
        super(ManagedPipelineJob, self).__init__(mongodb)
        # self._enforce_auth = True
        self.manager = manager_id
        self.nonce = update_nonce
        self.cancelable = True

        self.actor_id = None
        self.archive_path = None
        self.data = None
        self.exec_id = None
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

        for param, required, key, default, store, link in self.JOB_PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Job parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default

            if kval is not None:
                resp = self.__get_stored_doc(store, key, kval)
                if resp is None:
                    raise ManagedPipelineJobError(
                        'Failed to verify {}:{} exists store {}'.format(
                            param, kval, store))
                else:
                    uuidval = resp.get('uuid')
                    setattr(self, param, uuidval)
                    relations[link].append(uuidval)
        for rel, val in relations.items():
            setattr(self, rel, val)

        self.__set_archive_path(*args, **kwargs)

    def setup(self, data={}):
        """Finish initializing the manager

        Args: data (dict, optional): Override or set value for job data

        Returns:
            object: ``self``
        """
        setattr(self, 'data', data)
        job_document = {'pipeline_uuid': self.pipeline_uuid,
                        'archive_path': self.archive_path,
                        'data': self.data,
                        'session': self.session,
                        'actor_id': self.actor_id,
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

    def __set_archive_path(self, level_store='product', *args, **kwargs):

        ap = self.get_archive_path(level_store, *args, **kwargs)
        setattr(self, 'archive_path', ap)
        return self

    def get_archive_path(self, level_store='product', path=None, *args, **kwargs):

        # Allow user to pass `path at init time to create a custom archive_path`
        if path is not None:
            if not path.startswith('/'):
                raise ValueError('The override value passed for "path" must be an absolute path')

            return path

        if level_store == 'product':
            ap = self.archive_path_for_product(*args, **kwargs)
            # Compress path a bit by removing the dashes, which arise from
            # using UUID5 as path elements.
            ap = ap.replace('-', '')
        return ap

    def archive_path_for_product(self, *args, **kwargs):
        FIELDS = ('experiment_design_id', 'experiment_id', 'sample_id', 'measurement_id', 'pipeline_uuid')
        """Identity and order of document keys used to construct archive_path"""

        path_elements = ['/', 'products', 'v2']
        for field in FIELDS:
            if field in kwargs:
                path_elements.append(getattr(self, field))
        # raise Exception(path_elements)
        return os.path.join(*path_elements)

    def archive_path_for_reference(self, *args, **kwargs):
        raise NotImplementedError()

        FIELDS = ()
        path_elements = ['/', 'references']
        for field in FIELDS:
            if field in kwargs:
                path_elements.append(getattr(self, field))
        # raise Exception(path_elements)
        return os.path.join(*path_elements)

    def archive_path_for_upload(self, *args, **kwargs):
        raise NotImplementedError()

        FIELDS = ()
        path_elements = ['/', 'uploads']
        for field in FIELDS:
            if field in kwargs:
                path_elements.append(getattr(self, field))
        # raise Exception(path_elements)
        return os.path.join(*path_elements)

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
