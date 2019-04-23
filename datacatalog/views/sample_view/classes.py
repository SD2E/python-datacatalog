from ..common import MongoAggregation, MongoViewDocument

class ExperimentViewDocument(MongoViewDocument):
    """Represents a document from the experiment view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(ExperimentViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ExperimentViewDocument):
    """Generic interface to ExperimentViewDocument"""
    pass
