from transitions import Machine
import datetime

class JobStateMachine(object):
    """Load and manage Job state from serialized record"""
    states = ['created', 'running', 'failed', 'finished','validating',
    'validated', 'rejected', 'finalized', 'retired']
    transitions = [
        {'trigger': 'run', 'source': ['created', 'running'], 'dest': 'running'},
        {'trigger': 'fail', 'source': '*', 'dest': 'failed'},
        {'trigger': 'finish', 'source': ['running', 'finished'], 'dest': 'finished'},
        {'trigger': 'validate', 'source': 'finished', 'dest': 'validating'},
        {'trigger': 'validated', 'source': 'validating', 'dest': 'validated'},
        {'trigger': 'reject', 'source': 'validating', 'dest': 'rejected'},
        {'trigger': 'finalize', 'source': 'validated', 'dest': 'finalized'},
        {'trigger': 'retire', 'source': [
            'failed', 'finished', 'validating', 'validated', 'validated', 'finalized'], 'dest': 'retired'}
    ]

    def __init__(self, jobdef={}, state='created'):
        ts = current_time()
        self.job = jobdef

        # Add history key if not present, assuming this is a new record
        if 'history' not in self.job:
            self.job['history'] = [{'created': ts}]

        self.last_event = None

        self.machine = Machine(
            model=self, states=JobStateMachine.states,
            transitions=JobStateMachine.transitions,
            initial=state,
            auto_transitions=False,
            after_state_change='update_history')

    def history(self):
        return self.job.get('history', [])

    def update_history(self):
        ts = current_time()
        history_entry = {}
        history_entry[self.state] = ts
        self.job['history'].append(history_entry)
        self.last_event = self.state



def current_time():
    return datetime.datetime.utcnow()
