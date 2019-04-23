from ..common import MongoAggregation, MongoViewDocument

class ProductFileViewDocument(MongoViewDocument):
    """Represents a document from the upload view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(ProductFileViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ProductFileViewDocument):
    """Generic interface to ProductFileViewDocument"""
    pass
