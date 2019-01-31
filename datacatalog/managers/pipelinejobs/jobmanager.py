import arrow
import copy
import json
import os
import re
import sys
import validators
import logging
from pprint import pprint
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
        ('uuid', False, 'uuid', None)]

    def __init__(self, mongodb, agave=None, *args, **kwargs):
        self.cancelable = False
        self.job = None
        self._enforce_auth = False
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
        pass

    def cancel(self):
        """Cancel the job, deleting it from the system
        """
        try:
            if self.uuid is None:
                raise ValueError('Job UUID cannot be empty')
            if getattr(self, 'cancelable') is not False:
                self.stores['pipelinejob'].delete(self.uuid, self.token, soft=False)
                self.job = None
                return self.job
            else:
                raise ManagedPipelineJobError(
                    'Cannot cancel a job once it is running. Send a "fail" event instead.')
        except Exception as cexc:
            raise ManagedPipelineJobError(cexc)

    def handle(self, event_name, data={}, token=None):
        """Handle a named event
        """
        htoken = getattr(self, 'token', token)
        try:
            self.job = self.stores['pipelinejob'].handle({
                'name': event_name.lower(),
                'uuid': self.uuid,
                'token': htoken,
                'data': data})
            if getattr(self, 'cancelable'):
                setattr(self, 'cancelable', False)
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
        return self.handle('fail', data, token=token)

    def finish(self, data={}, token=None):
        """Wrapper for **finish**
        """
        return self.handle('finish', data, token=token)

    def index(self, data={}, token=None):
        """Wrapper for **index**
        """
        return self.handle('index', data, token=token)

    def indexed(self, data={}, token=None):
        """Wrapper for **indexed**
        """
        return self.handle('indexed', data, token=token)

    def reset(self, data={}, token=None):
        """Wrapper for **reset**
        """
        # Send the event w token. On success,
        # Do the archive_path delete action, which will be
        # a folder delete followed by recreate for speed. Then,
        # check contents are empty, and return resp if
        # all is OK.
        # TODO - Determine where to put check for admin token
        return self.handle('reset', data, token=token)

    def ready(self, data={}, token=None):
        """Wrapper for **ready*
        """
        return self.handle('ready', data, token=token)

    def serialize_data(self):
        """Serializes self.data into a minified string
        """
        return json.dumps(getattr(self, 'data', {}),
                          sort_keys=True,
                          separators=(',', ':'))
