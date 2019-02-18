from ..basestore import HeritableDocumentSchema
from ..basestore import msec_precision

class PipelineDocument(HeritableDocumentSchema):
    """Defines a compute or ETL pipeline"""

    def __init__(self, inheritance=True, **kwargs):
        super(PipelineDocument, self).__init__(inheritance, **kwargs)
        self.update_id()
