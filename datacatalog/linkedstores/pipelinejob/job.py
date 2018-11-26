
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

from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, ExtensibleAttrDict
from .schema import JobDocument, HistoryEventDocument
from .fsm import JobStateMachine

class HistoryEntry(ExtensibleAttrDict):
    def __init__(self, entry):
        super(HistoryEntry, self).__init__(entry)

    def to_dict(self):
        return self.as_dict()

class PipelineJob(ExtensibleAttrDict):
    # Extend object with with event handling, state, and history management
    def __init__(self, job_document):
        super(PipelineJob, self).__init__(job_document)
        job_state = job_document.get('state', 'created').upper()
        self.enforce_auth = True
        # self._job_state_machine = JobStateMachine(state=job_state)
        setattr(self, '_job_state_machine', JobStateMachine(state=job_state))

    def new(self, data={}):
        event = {'name': 'create', 'uuid': self.uuid, 'data': self.data}
        self.handle(event)
        return self

    def handle(self, event, opts={}):
        try:
            # EventResponse document - holds FSM state and last event
            edoc = self._job_state_machine.handle(event['name'].lower(), opts)
        except Exception as hexc:
            raise
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
        # if event['name'] != 'create':
        #     sys.exit(0)
        return self

    def gethistory(self):
        return getattr(self, 'history')

    # def to_dict(self):
    #     pr = dict()
    #     for name in self.dir():
    #         value = getattr(self, name)
    #         if not name.startswith('_') and not inspect.ismethod(value):
    #             pr[name] = value
    #     return pr

    def to_dict(self):
        d = self.as_dict()
        del d['_job_state_machine']
        return d
