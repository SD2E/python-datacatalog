from ..common import MongoAggregation, MongoViewDocument

class PipelineJobViewDocument(MongoViewDocument):
    """Represents a document from the pipelinejob view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(PipelineJobViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(PipelineJobViewDocument):
    """Generic interface to PipelineJobViewDocument"""
    pass
