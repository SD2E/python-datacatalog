from datacatalog.linkedstores.basestore import (LinkedStore, SoftDelete, JSONSchemaCollection)
from .document import StructuredRequestSchema, StructuredRequestDocument
from anaconda_project import status
from ...utils import time_stamp, msec_precision

class StructuredRequestStore(SoftDelete, LinkedStore):
    """Manage storage and retrieval of StructuredRequest documents"""

    def __init__(self, mongodb, config={}, session=None, agave=None, **kwargs):
        super(StructuredRequestStore, self).__init__(mongodb, config, session)
        schema = StructuredRequestSchema(**kwargs)
        super(StructuredRequestStore, self).update_attrs(schema)
        self._enforce_auth = True
        self.setup(update_indexes=kwargs.get('update_indexes', False))
    
    def update_request_status_for_experiment(self, experiment_id, key, state, path=None):
        query={}
        query['experiment_id'] = experiment_id
        matches = ref_store.query(query)
        
        # There should be at most one match
        if matches.count() == 0:
            return False
        else:
            structured_request = matches[0]

        if "status" not in structured_request:
            structured_request["status"] = {}
        
        structured_request["status"][key] = {
            "state": state,
            "last_updated": msec_precision(time_stamp()),
            "path": path
        }
        
        self.add_update_document(structured_request, strategy=strategies.REPLACE)
        
        return True
        
    def update_request_with_status(self, structured_request, key, state, path=None):

        if "status" not in structured_request:
            structured_request["status"] = {}
        
        structured_request["status"][key] = {
            "state": state,
            "last_updated": msec_precision(time_stamp()),
            "path": path
        }
        
        self.add_update_document(structured_request, strategy=strategies.REPLACE)        

class StoreInterface(StructuredRequestStore):
    pass
