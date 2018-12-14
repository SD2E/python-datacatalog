from ..common import MongoAggregation, MongoViewDocument

class ScienceTableDocument(MongoViewDocument):
    _index = True

    def __init__(self, inheritance=False, **kwargs):
        super(ScienceTableDocument, self).__init__(
            inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ScienceTableDocument):
    pass
