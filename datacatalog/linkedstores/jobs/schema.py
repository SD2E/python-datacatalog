from ..basestore import HeritableDocumentSchema
from ..basestore import msec_precision

class JobDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=True, **kwargs):
        super(JobDocument, self).__init__(inheritance, **kwargs)
        self.update_id()
