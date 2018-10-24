
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *
from builtins import object

import datetime
import functools
import inspect

from attrdict import AttrDict
from pprint import pprint
from transitions import Machine

class JobFSM(AttrDict):
    FILTER_KEYS = ('_id', 'transitions', 'states', 'state', 'machine')
    FILTER_TYPES = (functools.partial)
    pass

class JobStateMachine(object):
    """Load and manage Job state from serialized record"""
    states = ['CREATED', 'RUNNING', 'FAILED', 'FINISHED', 'VALIDATING',
              'VALIDATED', 'REJECTED', 'FINALIZED', 'RETIRED']
    transitions = [
        {'trigger': 'run', 'SOURCE': ['CREATED', 'RUNNING'], 'DEST': 'RUNNING'},
        {'trigger': 'update', 'SOURCE': ['RUNNING'], 'DEST': '='},
        {'trigger': 'fail', 'SOURCE': '*', 'DEST': 'FAILED'},
        {'trigger': 'finish', 'SOURCE': ['RUNNING', 'FINISHED'], 'DEST': 'FINISHED'},
        {'trigger': 'validate', 'SOURCE': 'FINISHED', 'DEST': 'VALIDATING'},
        {'trigger': 'validated', 'SOURCE': 'VALIDATING', 'DEST': 'VALIDATED'},
        {'trigger': 'reject', 'SOURCE': 'VALIDATING', 'DEST': 'REJECTED'},
        {'trigger': 'finalize', 'SOURCE': 'VALIDATED', 'DEST': 'FINALIZED'},
        {'trigger': 'retire', 'SOURCE': [
            'FAILED', 'FINISHED', 'VALIDATING', 'VALIDATED', 'VALIDATED', 'FINALIZED'], 'DEST': 'RETIRED'}
    ]

    def __init__(self, jobdef, status='created'):

        self.data = {}
        ts = current_time()
        for k in jobdef:
            setattr(self, k, jobdef.get(k, None))

        # These will be empty if jobdef refers to a newly created job
        if 'history' not in jobdef:
            self.history = [{'CREATE': {'date': ts, 'data': None}}]
        if 'status' not in jobdef:
            self.status = 'CREATED'
        if 'last_event' not in jobdef:
            self.last_event = 'CREATE'
        if 'updated' not in jobdef:
            self.updated = ts

        initial_state = status
        if getattr(self, 'status') is not None:
            initial_state = getattr(self, 'status')
        self.machine = Machine(
            model=self, states=JobStateMachine.states,
            transitions=JobStateMachine.transitions,
            initial=initial_state.lower(),
            auto_transitions=False,
            after_state_change='update_history')

    def handle(self, event_name, opts={}):
        eventfn = event_name.lower()
        eventname = event_name.upper()
        vars(self)[eventfn](opts, event=eventname)
        return self

    def get_history(self):
        return self.history

    def update_history(self, opts, event):
        ts = current_time()
        history_entry = {}
        history_entry[str(event).upper()] = {'date': ts, 'data': opts}
        self.history.append(history_entry)
        self.status = self.state
        self.last_event = event.upper()
        self.updated = ts

    @classmethod
    def get_states(cls):
        return sorted(cls.states)

    @classmethod
    def get_events(cls):
        events = list()
        for t in cls.transitions:
            events.append(t['trigger'])
        events = sorted(events)
        return events

    def as_dict(self):
        pr = {}
        for name in dir(self):
            if name not in JobFSM.FILTER_KEYS:
                value = getattr(self, name)
                if not isinstance(value, JobFSM.FILTER_TYPES):
                    if not name.startswith('__') and not inspect.ismethod(value):
                        pr[name] = value
        return JobFSM(pr)

def current_time():
    return datetime.datetime.utcnow()
