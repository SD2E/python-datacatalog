from ..basestore import HeritableDocumentSchema
from ..basestore import msec_precision

class FixityDocument(HeritableDocumentSchema):
    """Schema-driven document to represent file fixity"""

    def __init__(self, inheritance=True, **kwargs):
        super(FixityDocument, self).__init__(inheritance, **kwargs)
        self.update_id()
