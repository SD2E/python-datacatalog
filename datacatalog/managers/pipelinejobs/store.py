
import os
import sys
from pprint import pprint
from ... import identifiers
# from ...linkedstores.pipelinejob import PipelineJobStore
from ..common import Manager
from ...tokens import get_token
from ...linkedstores.basestore import DEFAULT_LINK_FIELDS as LINK_FIELDS

# Required to init
# pipeline_uuid
# data

class ManagedPipelineJobError(Exception):
    pass

class ManagedPipelineJob(Manager):

    MGR_PARAMS = [('actor_id', False, 'actor_id', None),
                  ('agent', False, 'actor_id', None),
                  ('task', False, 'task', None),
                  ('exec_id', False, 'task', None),
                  ('session', False, 'session', None),
                  ('data', False, 'data', {})]

    JOB_PARAMS = [('experiment_design_id', False, 'experiment_design_id', None, 'experiment_design', 'derived_from'),
                  ('experiment_id', True, 'experiment_id', None, 'experiment', 'derived_from'),
                  ('sample_id', True, 'sample_id', None, 'sample', 'derived_from'),
                  ('measurement_id', False, 'measurement_id', None, 'measurement', 'derived_from'),
                  ('pipeline_uuid', True, 'uuid', None, 'pipeline', 'generated_by')]

    def __init__(self, mongodb, config={}, pipeline_settings={}, *args, **kwargs):
        super(ManagedPipelineJob, self).__init__(mongodb, *args)

        # self._enforce_auth = True
        self.archive_path = None
        self.data = None
        self.pipeline_uuid = None
        self.actor_id = None
        self.exec_id = None
        self.session = None

        self.manager = None
        self.nonce = None
        self.cancelable = True

        for param, required, key, default in self.MGR_PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Manager parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default
                setattr(self, param, kval)

        relations = dict()
        for lf in LINK_FIELDS:
            relations[lf] = list()

        for param, required, key, default, store, link in self.JOB_PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Job parameter "{}" is required'.format(param))
            if kval is not None:
                resp = self.get_stored_doc(store, key, kval)
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
        setattr(self, 'data', data)
        job_document = {'pipeline_uuid': self.pipeline_uuid,
                        'archive_path': self.archive_path,
                        'data': self.data,
                        'session': self.session,
                        'actor_id': self.actor_id,
                        'session': self.session,
                        'child_of': self.child_of,
                        'derived_from': self.derived_from,
                        'generated_by': self.generated_by
                        }
        new_job = self.stores['pipelinejob'].create(job_document)
        token = get_token(new_job['_salt'], self.stores['pipelinejob'].get_token_fields(new_job))

        setattr(self, 'uuid', new_job['uuid'])
        setattr(self, 'job', new_job)
        setattr(self, 'token', token)
        setattr(self, 'callback', self.get_webhook())
        # raise Exception(self.job)
        return self

    def run(self, data={}):

        self.job = self.stores['pipelinejob'].handle({
            'name': 'run',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})
        setattr(self, 'cancelable', False)
        return self.job

    def update(self, data={}):

        self.job = self.stores['pipelinejob'].handle({
            'name': 'update',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})

        setattr(self, 'cancelable', False)
        return self.job

    def fail(self, data={}):

        self.job = self.stores['pipelinejob'].handle({
            'name': 'fail',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})
        setattr(self, 'cancelable', False)
        return self.job

    def finish(self, data={}):

        self.job = self.stores['pipelinejob'].handle({
            'name': 'finish',
            'uuid': self.uuid,
            'token': self.token,
            'data': data})
        setattr(self, 'cancelable', False)
        return self.job

    def cancel(self):
        if getattr(self, 'cancelable') is not False:
            self.stores['pipelinejob'].delete(self.uuid, self.token, soft=False)
            self.job = None
            return self.job
        else:
            raise ManagedPipelineJobError('Cannot cancel a job once it is running. Send a "fail" event instead.')

    def __set_archive_path(self, level='product', *args, **kwargs):

        ap = self.get_archive_path(level, *args, **kwargs)
        setattr(self, 'archive_path', ap)
        return self

    def get_archive_path(self, level='product', path=None, *args, **kwargs):

        # Allow user to pass `path at init time to create a custom archive_path`
        if path is not None:
            if not path.startswith('/'):
                raise ValueError('The override value passed for "path" must be an absolute path')

            return path

        if level == 'product':
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

    def get_stored_doc(self, store, key, val):
        return self.stores[store].coll.find_one({key: val})

    def get_webhook(self):
        """Return a webhook to pipeline-jobs-manager actorId, which has a world EXECUTE nonce"""

        api_server = 'https://api.sd2e.org'
        # api_server = self.settings.pipelines.api_server

        uri = '{}/actors/v2/{}/messages?x-nonce={}&token={}&uuid={}'.format(
            api_server, self.manager, self.nonce, self.token, self.uuid)
        return uri
