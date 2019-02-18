from ..common import MongoAggregation, MongoViewDocument

class ScienceViewDocument(MongoViewDocument):
    """Represents a document from the science_view view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(ScienceViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ScienceViewDocument):
    """Generic interface to ScienceViewDocument"""
    pass
