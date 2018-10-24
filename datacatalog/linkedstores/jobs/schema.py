from ..basestore import HeritableDocumentSchema
from ..basestore import msec_precision

class JobDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=True, **kwargs):
        super(JobDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class EventDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=False, filename='pipelinejob_event.json', ** kwargs):
        super(EventDocument, self).__init__(inheritance, **kwargs)
        self.update_id()
