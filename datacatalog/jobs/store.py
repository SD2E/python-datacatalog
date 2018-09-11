import uuid
from ..basestore import *
from .fsm import JobStateMachine
class JobCreateFailure(Exception):
    pass

class JobUpdateFailure(Exception):
    pass

class JobStore(BaseStore):
    """Create and manage job record and state"""

    def __init__(self, mongodb, config, session=None):
        super(JobStore, self).__init__(mongodb, config, session)
        coll = config['collections']['jobs']
        if config['debug']:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()

    def create_job(self):
        pass

    def handle_job_event(self, uuid, event, options={}):
        pass

    def delete_job(self, uuid):
        pass
