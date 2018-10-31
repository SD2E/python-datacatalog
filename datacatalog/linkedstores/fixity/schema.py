from ..basestore import HeritableDocumentSchema
from ..basestore import msec_precision

class FixityDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=True, **kwargs):
        super(FixityDocument, self).__init__(inheritance, **kwargs)
        self.update_id()
