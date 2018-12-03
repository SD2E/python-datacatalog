
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object

import copy
import inspect
import json
import os
import sys
from attrdict import AttrDict
from pprint import pprint

from ..basestore import LinkedStore, CatalogError, CatalogUpdateFailure, HeritableDocumentSchema, ExtensibleAttrDict
from .schema import JobDocument, HistoryEventDocument
from .fsm import JobStateMachine

class HistoryEntry(ExtensibleAttrDict):
    def __init__(self, entry):
        super(HistoryEntry, self).__init__(entry)

    def to_dict(self):
        return self.as_dict()

class PipelineJobError(CatalogError):
    """Error occured within scope of a PipelineJob"""
    pass

class PipelineJobDocument(HeritableDocumentSchema):
    """Defines a PipelineJob in terms of its schema"""

    def __init__(self, inheritance=True, **kwargs):
        super(PipelineJobDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class PipelineJob(PipelineJobDocument):
    """Defines a PipelineJob, including not just its schema, but also how its state and history are managed."""

    MGR_PARAMS = [('agent', True, 'agent', None),
                  ('task', False, 'task', None),
                  ('session', False, 'session', None)]

    JOB_PARAMS = [('experiment_design_id', False, 'experiment_design_id', None, 'experiment_design'),
                  ('experiment_id', True, 'experiment_id', None, 'experiment'),
                  ('sample_id', True, 'sample_id', None, 'sample'),
                  ('measurement_id', False, 'measurement_id', None, 'measurement'),
                  ('data', True, 'data', {}, 'job')]

    def __init__(self, job_document, **kwargs):
        super(PipelineJob, self).__init__(**kwargs)

        # A PipelineJob is different from the pure document-driven
        # objects in other LinkedStores: We need to be able to persistently
        # access various fields in the job and the core schema is not expcted
        # to change, so it has a lot more defined slots, some of which map to
        # the schema and others that are purely internal to event handling and
        # state management processes.

        self._job_state_machine = None
        """An instance of a Python transitions state machine"""
        self.state = None
        """Current state of the job"""
        self.last_event = None
        """Last event processed by the jobs internal state manager"""
        self.updated = None
        """When the job last was updated by receiving an event"""
        self.history = None
        """Holds a list of ``HistoryEntry`` objects arising from event handling"""
        self.archive_path = None
        """Absolute path managed by the jobs process(es)"""
        self.data = None
        """Arbitrary but informative data passed when the job was created"""
        self.uuid = None
        """The job's TypedUUID"""

        self._enforce_auth = True
        """Whether to enforce token authorization to update the job"""

        job_state = job_document.get('state', 'created').upper()
        setattr(self, '_job_state_machine', JobStateMachine(state=job_state))

    def new(self, data={}):
        event = {'name': 'create', 'uuid': self.uuid, 'data': self.data}
        self.handle(event)
        return self

    # def setup(self, data={}):
    #     self.data = data
    #     return self

    def handle(self, event, opts={}):
        try:
            # EventResponse document - holds FSM state and last event
            edoc = self._job_state_machine.handle(event['name'].lower(), opts)
        except Exception as hexc:
            raise PipelineJobError(hexc)
        # Event was handled
        # Set job properties
        setattr(self, 'state', edoc['state'])
        setattr(self, 'last_event', edoc['last_event'])
        # Extend job history
        new_hist = {'date': HistoryEventDocument.time_stamp(),
                    'data': event.get('data', None),
                    'name': event.get('name')}
        hdoc = HistoryEntry(new_hist).to_dict()
        history = getattr(self, 'history', [])
        history.append(hdoc)
        setattr(self, 'updated', new_hist['date'])
        setattr(self, 'history', history)
        return self

    def gethistory(self):
        """Top-level function to return the job's history"""
        return getattr(self, 'history')

    def to_dict(self):
        """Render the job as a dictionary suitable for serialization"""
        d = self.as_dict()
        del d['_job_state_machine']
        return d

    def get_archive_path(level='product', *args, **kwargs):
        pass
