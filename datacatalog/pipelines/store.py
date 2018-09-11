import uuid
from ..basestore import *
from .utils import components_to_document, components_document_to_id

class PipelineUpdateFailure(CatalogUpdateFailure):
    pass

class PipelineStore(BaseStore):
    """Create and manage expts metadata
    Records are linked with samples via sample-specific uuid"""

    def __init__(self, mongodb, config, session=None):
        super(PipelineStore, self).__init__(mongodb, config, session)
        coll = config['collections']['pipelines']
        if config['debug']:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()

    def update_properties(self, dbrec):
        ts = current_time()
        properties = dbrec.get('properties', {})
        properties['created_date'] = properties.get('created_date', ts)
        if properties.get('modified_date', ts) >= ts:
            properties['modified_date'] = ts
        properties['revision'] = properties.get('revision', 0) + 1
        dbrec['properties'] = data_merge(dbrec['properties'], properties)
        return dbrec

    def create_pipeline(self, components, name=None, description=None):
        ts = current_time()
        doc = components_to_document(components)
        doc_uuid = components_document_to_id(doc)
        pipe_rec = {'uuid': doc_uuid,
                    'properties': {'created_date': ts,
                                   'modified_date': ts,
                                   'revision': 0},
                    'document': doc,
                    'name': name,
                    'description': description}
        try:
            result = self.coll.insert_one(pipe_rec)
            return self.coll.find_one({'_id': result.inserted_id})
        except Exception as exc:
            raise PipelineUpdateFailure(
                'Failed to create pipeline record', exc)

    def delete_pipeline(self, uuid):
        '''Delete record by UUID'''
        if isinstance(uuid, str):
            uuid = text_uuid_to_binary(uuid)
        try:
            return self.coll.remove({'uuid': uuid})
        except Exception as exc:
            raise PipelineUpdateFailure(
                'Failed to delete pipeline {}'.format(uuid), exc)

