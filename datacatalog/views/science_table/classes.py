from ..common import MongoAggregation, MongoViewDocument

class ScienceTableDocument(MongoViewDocument):
    """Represents a document from the science_table view"""

    _index = True

    def __init__(self, inheritance=False, **kwargs):
        super(ScienceTableDocument, self).__init__(
            inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ScienceTableDocument):
    """Generic interface to ScienceTableDocument"""
    pass
