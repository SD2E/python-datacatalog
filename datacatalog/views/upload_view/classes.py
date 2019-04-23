from ..common import MongoAggregation, MongoViewDocument

class UploadFileViewDocument(MongoViewDocument):
    """Represents a document from the upload view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(UploadFileViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(UploadFileViewDocument):
    """Generic interface to UploadFileViewDocument"""
    pass
