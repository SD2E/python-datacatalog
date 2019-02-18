from ..common import MongoAggregation, MongoViewDocument

class PipelineJobsTableDocument(MongoViewDocument):
    """Represents a document from the pipelinejobs_table view"""

    _index = True

    def __init__(self, inheritance=False, **kwargs):
        super(PipelineJobsTableDocument, self).__init__(
            inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(PipelineJobsTableDocument):
    """Generic interface to PipelineJobsTableDocument"""
    pass
