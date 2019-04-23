from ..common import MongoAggregation, MongoViewDocument

class SampleViewDocument(MongoViewDocument):
    """Represents a document from the sample view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(SampleViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(SampleViewDocument):
    """Generic interface to SampleViewDocument"""
    pass
