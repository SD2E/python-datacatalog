import functools
import inspect

from attrdict import AttrDict
from pprint import pprint
from transitions import Machine

__all__ = ['JobStateMachine', 'EventResponse']

STATE_DEFS = [('CREATED', 'Job inputs and configuration has been defined'),
              ('RUNNING', 'Job is actively processing data'),
              ('FAILED', 'Job did not complete successfully'),
              ('FINISHED', 'Job has completed processing and outputs are archived'),
              ('INDEXING', 'Job outputs are being associated with project metadata'),
              ('VALIDATING', 'Job outputs are being assessed for correctness'),
              ('VALIDATED', 'Job outputs were determined to be correct'),
              ('REJECTED', 'Job outputs are invalid and should not be used'),
              ('FINALIZED', 'Job outputs are validated and ready for general use'),
              ('RETIRED', 'Job and outputs should no longer be used')]

EVENT_DEFS = [('create', 'Create a new job'),
              ('run', 'Mark the job as "running"'),
              ('update', 'Append an information item to the job history'),
              ('resource', 'Note resource marshalling activity in the job history'),
              ('fail', 'Permanently mark the job as failed'),
              ('finish', 'Mark the job as complete'),
              ('index', 'Index the job outputs'),
              ('indexed', 'Mark that the indexing task is complete'),
              ('validate', 'Mark the job as under validation'),
              ('validated', 'Mark that validation has completed'),
              ('finalize', 'Mark the job and its outputs as suitable for use'),
              ('reject', 'Mark the job and its outputs as unsuitable for use'),
              ('retire', 'Mark job and its outputs as retired/deprecated')]

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
    states = [state_name for state_name, state_desc in STATE_DEFS]
    transitions = [
        {'trigger': 'create', 'source': 'CREATED', 'dest': 'CREATED'},
        {'trigger': 'run', 'source': ['CREATED', 'RUNNING'], 'dest': 'RUNNING'},
        {'trigger': 'update', 'source': ['RUNNING', 'VALIDATING', 'INDEXING'], 'dest': '='},
        {'trigger': 'resource', 'source': ['CREATED', 'RUNNING'], 'dest': '='},
        {'trigger': 'fail', 'source': ['RUNNING', 'VALIDATING', 'INDEXING'], 'dest': 'FAILED'},
        {'trigger': 'finish', 'source': ['RUNNING', 'FINISHED'], 'dest': 'FINISHED'},
        {'trigger': 'index', 'source': ['INDEXING', 'FINISHED'], 'dest': 'INDEXING'},
        {'trigger': 'indexed', 'source': ['FINISHED', 'INDEXING'], 'dest': 'FINISHED'},
        {'trigger': 'validate', 'source': ['FINISHED', 'VALIDATED'], 'dest': 'VALIDATING'},
        {'trigger': 'validated', 'source': ['VALIDATED', 'VALIDATING'], 'dest': 'VALIDATED'},
        {'trigger': 'reject', 'source': 'VALIDATING', 'dest': 'REJECTED'},
        {'trigger': 'finalize', 'source': 'VALIDATED', 'dest': 'FINALIZED'},
        {'trigger': 'retire', 'source': ['REJECTED', 'FINALIZED'], 'dest': 'RETIRED'}
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
