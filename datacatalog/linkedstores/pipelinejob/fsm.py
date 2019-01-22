import functools
import inspect

from attrdict import AttrDict
from pprint import pprint
from transitions import Machine

STATE_DEFS = [('CREATED', 'Job record has been created'),
              ('RUNNING', 'Job is actively processing data'),
              ('FAILED', 'Something caused the job to fail'),
              ('FINISHED', 'Job has completed processing and results are archived'),
              ('INDEXING', 'Job outputs are being associated with project metadata'),
              ('VALIDATING', 'Job outputs are in being checked for correctness'),
              ('VALIDATED', 'Job outputs were determined to be correct'),
              ('REJECTED', 'Job outputs were determined to be incorrect'),
              ('FINALIZED', 'Job outputs are suitable for general use'),
              ('RETIRED', 'Job outputs have been superceded by another')]

EVENT_DEFS = [('create', 'Create a job'),
              ('run', 'Mark job as "running"'),
              ('update', 'Log a message in job history'),
              ('resource', 'Note resource marshalling in job history'),
              ('fail', 'Permanently mark the job as failed'),
              ('finish', 'Mark the job as complete'),
              ('index', 'Index the job outputs'),
              ('indexed', 'Note that the job indexing is complete'),
              ('validate', 'Note that the job is being validated'),
              ('validated', 'Note that validation has completed'),
              ('finalize', 'Mark job outputs as ready for general use'),
              ('reject', 'Mark job outputs as invalid'),
              ('retire', 'Mark job as retired from active usage')]

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
        {'trigger': 'update', 'source': ['RUNNING'], 'dest': '='},
        {'trigger': 'resource', 'source': ['CREATED', 'RUNNING'], 'dest': '='},
        {'trigger': 'fail', 'source': '*', 'dest': 'FAILED'},
        {'trigger': 'finish', 'source': ['RUNNING', 'FINISHED'], 'dest': 'FINISHED'},
        {'trigger': 'index', 'source': ['FINISHED'], 'dest': 'INDEXING'},
        {'trigger': 'indexed', 'source': ['INDEXING'], 'dest': 'FINISHED'},
        {'trigger': 'validate', 'source': 'FINISHED', 'dest': 'VALIDATING'},
        {'trigger': 'validated', 'source': 'VALIDATING', 'dest': 'VALIDATED'},
        {'trigger': 'reject', 'source': 'VALIDATING', 'dest': 'REJECTED'},
        {'trigger': 'finalize', 'source': 'VALIDATED', 'dest': 'FINALIZED'},
        {'trigger': 'retire', 'source': ['INDEXING' 'FAILED',
                                         'FINISHED', 'VALIDATING', 'VALIDATED',
                                         'VALIDATED', 'FINALIZED'], 'dest': 'RETIRED'}
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
