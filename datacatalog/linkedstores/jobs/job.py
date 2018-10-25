
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

from .schema import JobDocument, HistoryEventDocument
from .fsm import JobStateMachine

class PipelineJob(JobDocument):
    # Extend passive schema-based doc with event handling, state, and history management
    def __init__(self, job_document):
        self._job_state_machine = JobStateMachine(state=job_document.get('state'))

    def handle(self, event, opts={}):
        try:
            # EventResponse document - holds FSM state and last event
            edoc = self._job_state_machine.handle(event, opts=opts)
        except Exception as hexc:
            raise

        # Event was handled
        # Set job properties
        setattr(self, 'state', edoc['state'])
        setattr(self, 'last_event', edoc['last_event'])
        # Extend job history
        new_hist = {'created': HistoryEventDocument.time_stamp(),
                    'data': event.get('data', None),
                    'name': event.get('name')}
        hdoc = HistoryEventDocument(new_hist).to_dict()
        history = getattr(self, '_history', [])
        history.append(hdoc)
        setattr(self, '_history', history)
        return self

    def get_history(self):
        return getattr(self, '_history')

    def to_dict(self):
        pr = dict()
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('_') and not inspect.ismethod(value):
                pr[name] = value
        return pr
