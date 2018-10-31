import functools
import inspect

from attrdict import AttrDict
from pprint import pprint
from transitions import Machine

class EventResponse(AttrDict):
    PARAMS = [('last_event', True, None),
              ('state', True, None)]

    def __init__(self, **kwargs):
        for attr, req, default in self.PARAMS:
            if req:
                setattr(self, attr, kwargs.get(attr, default))
            else:
                setattr(self, attr, None)

class JobStateMachine(Machine):
    states = ['CREATED', 'RUNNING', 'FAILED', 'FINISHED', 'VALIDATING',
              'VALIDATED', 'REJECTED', 'FINALIZED', 'RETIRED']
    transitions = [
        {'trigger': 'create', 'source': 'CREATED', 'dest': 'CREATED'},
        {'trigger': 'run', 'source': ['CREATED', 'RUNNING'], 'dest': 'RUNNING'},
        {'trigger': 'update', 'source': ['RUNNING'], 'dest': '='},
        {'trigger': 'fail', 'source': '*', 'dest': 'FAILED'},
        {'trigger': 'finish', 'source': ['RUNNING', 'FINISHED'], 'dest': 'FINISHED'},
        {'trigger': 'validate', 'source': 'FINISHED', 'dest': 'VALIDATING'},
        {'trigger': 'validated', 'source': 'VALIDATING', 'dest': 'VALIDATED'},
        {'trigger': 'reject', 'source': 'VALIDATING', 'dest': 'REJECTED'},
        {'trigger': 'finalize', 'source': 'VALIDATED', 'dest': 'FINALIZED'},
        {'trigger': 'retire', 'source': [
            'FAILED', 'FINISHED', 'VALIDATING', 'VALIDATED', 'VALIDATED', 'FINALIZED'], 'dest': 'RETIRED'}
    ]

    def __init__(self, state=states[0]):
        Machine.__init__(self, states=self.states, transitions=self.transitions, initial=state, auto_transitions=False)

    def handle(self, event_name, event_opts={}):
        eventfn = event_name.lower()
        eventname = event_name
        vars(self)[eventfn](event_opts, event=eventname)
        resp = EventResponse(last_event=event_name, state=self.state)
        return resp

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
