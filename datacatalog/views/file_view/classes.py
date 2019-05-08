from ..common import MongoAggregation, MongoViewDocument

class FixtyFileViewDocument(MongoViewDocument):
    """Represents a document from the upload view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(FixtyFileViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(FixtyFileViewDocument):
    """Generic interface to FixtyFileViewDocument"""
    pass
