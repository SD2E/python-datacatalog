import arrow
import copy
import json
import os
import re
import sys
import validators
import logging
from pprint import pprint
from ...tokens import validate_admin_token
from ...tokens.admin import internal_get_admin_token
from ...tokens import admin
from ..common import Manager, data_merge
from .exceptions import ManagedPipelineJobError
from .config import DEFAULT_ARCHIVE_SYSTEM

class JobManager(Manager):
    PARAMS = [
        ('archive_path', False, 'archive_path', None),
        ('archive_patterns', False, 'archive_patterns', []),
        ('archive_system', False, 'archive_system', DEFAULT_ARCHIVE_SYSTEM),
        ('pipeline_uuid', False, 'pipeline_uuid', None),
        ('token', False, 'token', None),
        ('uuid', False, 'uuid', None),
        ('state', False, 'state', None)]
    ADMIN_EVENTS = ['reset', 'ready', 'delete', 'purge']

    def __init__(self, mongodb, agave=None, *args, **kwargs):
        self.cancelable = False
        self.job = None
        self._enforce_auth = True
        super(JobManager, self).__init__(mongodb, agave)
        # Read in core kwargs per PARAMS
        for param, required, key, default in self.PARAMS:
            kval = kwargs.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError('Parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default
            setattr(self, key, kval)

    def setup(self, *args, **kwargs):
        return self

    def attach(self, token=None):
        """Simplified proxy for load

        Materializes just enough of the job to interact with it
        """
        return self.load(job_uuid=self.uuid, token=token)

    def load(self, job_uuid=None, token=None):
        """Load up an JobManager instance for the given UUID

        This fuction is the opposite of ``setup()``. It populates a minimum
        attribute set from the current contents of a job.

        Args:
            job_uuid (string): A known job TypedUUID
            token (string, optional): Update token for the job

        Raises:
            ManagedPipelineJobError is raised on any unrecoverable error

        Returns:
            object: ``self``
        """
        if job_uuid is None:
            job_uuid = getattr(self, 'uuid', None)
        if job_uuid is None:
            raise ManagedPipelineJobError('Unable to load job contents')
        loaded_job = self.stores['pipelinejob'].find_one_by_uuid(job_uuid)
        if loaded_job is None:
            raise ManagedPipelineJobError('No job {} was found'.format(job_uuid))
        for param, required, key, default in self.PARAMS:
            kval = loaded_job.get(param, None)
            if kval is None and required is True:
                raise ManagedPipelineJobError(
                    'Parameter "{}" is required'.format(param))
            else:
                if kval is None:
                    kval = default
            setattr(self, key, kval)
        return self

    def cancel(self, token=None):
        """Cancel the job, deleting it from the system
        """
        if token is not None:
            htoken = token
        else:
            htoken = getattr(self, 'token', None)
        try:
            if self.uuid is None:
                raise ValueError('Job UUID cannot be empty')
            if getattr(self, 'cancelable') is not False:
                self.stores['pipelinejob'].delete(self.uuid, htoken, soft=False)
                self.job = None
                return self.job
            else:
                raise ManagedPipelineJobError(
                    'Cannot cancel a job once it is running. Send a "fail" event instead.')
        except Exception as cexc:
            raise ManagedPipelineJobError(cexc)

    def delete(self, token=None):
        """Delete the job once, even if it has processed events
        """
        if token is not None:
            htoken = token
        else:
            htoken = getattr(self, 'token', None)
        try:
            if self.uuid is None:
                raise ValueError('Job UUID cannot be empty')
            else:
                self.stores['pipelinejob'].delete(self.uuid, htoken, soft=False)
                self.job = None
                for param, required, key, default in self.PARAMS:
                    setattr(self, param, None)
                return self
        except Exception as cexc:
            raise ManagedPipelineJobError(cexc)

    def handle(self, event_name, data={}, token=None, **kwargs):
        """Handle a named event
        """
        # Passed token >> current token to permit
        # passing admin token as an argument
        if token is None:
            htoken = getattr(self, 'token', None)
        else:
            htoken = token
        try:
            if event_name in self.ADMIN_EVENTS:
                validate_admin_token(htoken,
                                     key=admin.get_admin_key(),
                                     permissive=False)
            # HRM
            if getattr(self, 'uuid', None) is None:
                self.setup(update_indexes=kwargs.get('update_indexes', False))

            self.job = self.stores['pipelinejob'].handle({
                'name': event_name.lower(),
                'uuid': self.uuid,
                'token': htoken,
                'data': data})
            if getattr(self, 'cancelable'):
                setattr(self, 'cancelable', False)
            for param, required, key, default in self.PARAMS:
                setattr(self, param, self.job.get(param, None))
            return self.job
        except Exception as hexc:
            raise ManagedPipelineJobError(hexc)

    def run(self, data={}, token=None):
        """Wrapper for **run**
        """
        return self.handle('run', data, token=token)

    def resource(self, data={}, token=None):
        """Wrapper for **resource**
        """
        return self.handle('resource', data, token=token)

    def update(self, data={}, token=None):
        """Wrapper for **update**
        """
        return self.handle('update', data, token=token)

    def fail(self, data={}, token=None):
        """Wrapper for **fail**
        """
        # This lets job workflows simply call fail() if the job
        # has not yet started running. We could also allow CREATED
        # to go to FAILED, thus preserving history. To do that, we
        # need to back this code out and update the FSM
        if getattr(self, 'cancelable', False):
            return self.cancel(token=internal_get_admin_token())
        else:
            return self.handle('fail', data, token=token)

    def finish(self, data={}, token=None):
        """Wrapper for **finish**
        """
        return self.handle('finish', data, token=token)

    def index(self, data={}, token=None, **kwargs):
        """Wrapper for **index**
        """
        return self.handle('index', data, token=token)

    def indexed(self, data={}, token=None, **kwargs):
        """Wrapper for **indexed**
        """
        return self.handle('indexed', data, token=token)

    def reset(self, data={}, no_clear_path=False, token=None, permissive=False):
        """Wrapper for **reset**

        Note: This event encapsulates both the 'reset' and subsequent 'ready'
        event, as the resetting process needs to be thread-locked.
        """

        validate_admin_token(token, key=admin.get_admin_key(), permissive=False)
        resp = self.handle('reset', data, token=token)
        if not no_clear_path:
            self._clear_archive_path(permissive=permissive)
        # print('Sending READY')
        resp = self.handle('ready', data, token=token)
        return resp

    def ready(self, data={}, token=None):
        """Wrapper for **ready*
        """
        validate_admin_token(token, key=admin.get_admin_key(), permissive=False)
        return self.handle('ready', data, token=token)

    def serialize_data(self):
        """Serializes self.data into a minified string
        """
        return json.dumps(getattr(self, 'data', {}),
                          sort_keys=True,
                          separators=(',', ':'))

    def archive_uri(self):
        """Formats archive system and path into a URI
        """
        return 'agave://{}{}'.format(
            getattr(self, 'archive_system', 'NA'),
            getattr(self, 'archive_path', 'NA'))

    def __repr__(self):
        vals = list()
        vals.append('uuid: {}'.format(getattr(self, 'uuid')))
        vals.append('pipeline: {}'.format(getattr(self, 'pipeline_uuid')))
        vals.append('archive_uri: {}'.format(self.archive_uri()))
        return '\n'.join(vals)

    def _validate_clearable_archive_path(self, path, permissive=True):
        PREFIXES = ('/products/v2', '/sample/tacc-cloud')
        for p in PREFIXES:
            if path.startswith(p):
                return True
        if permissive:
            return False
        else:
            raise ValueError(
                'Only specific paths may be cleared: {}'.format(PREFIXES))

    def _clear_archive_path(self, mock=False, permissive=True):
        """Administratively clears a job's archive path

        Path is cleared quickly by deleting the directory then recreating it.
        Preview the actions to be taken by this function by passing
        ``mock=True`` as a parameter.

        Args:
            mock (bool, optional): Whether to simulate running the delete

        Raises: ManagedPipelineJobError is raised for any error state

        Returns: bool
        """
        try:
            ag_sys = getattr(self, 'archive_system', None)
            ag_path = getattr(self, 'archive_path', None)
            helper = self.stores['pipelinejob']._helper
            self._validate_clearable_archive_path(ag_path)
            if not helper.isdir(ag_path, storage_system=ag_sys):
                raise ValueError('Path does not appear to exist')

            if mock:
                print('clear_archive_path.mock.delete', ag_path, ag_sys)
                print('clear_archive_path.mock.mkdir', ag_path, ag_sys)
            else:
                helper.delete(ag_path, ag_sys)
                helper.mkdir(ag_path, ag_sys)
        except Exception as clexc:
            if permissive is False:
                raise ManagedPipelineJobError(clexc)
            else:
                return False
        return True
