import copy
import inspect
import json
import os
import sys
from attrdict import AttrDict
from pprint import pprint

from ...identifiers.typeduuid import generate as generate_uuid

from ..basestore import LinkedStore
from ..basestore import HeritableDocumentSchema, ExtensibleAttrDict
from ..basestore import DocumentAgaveClient
from ..basestore import CatalogError, CatalogUpdateFailure, AgaveError, AgaveHelperError

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
class PipelineJob(ExtensibleAttrDict, DocumentAgaveClient):
    # Extend object with with event handling, state, and history management
    def __init__(self, job_document, agave=None):
        super(PipelineJob, self).__init__(job_document)
        job_state = job_document.get('state', 'created').upper()
        # self._enforce_auth = True
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
                    'name': event.get('name'),
                    'uuid': generate_uuid(uuid_type='pipelinejob_event')}
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
        for k in ['_job_state_machine', '_helper']:
            try:
                del d[k]
            except KeyError:
                pass
        return d
