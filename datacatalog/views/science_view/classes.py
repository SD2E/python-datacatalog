from ..common import MongoAggregation, MongoViewDocument

class ScienceViewDocument(MongoViewDocument):
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(ScienceViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ScienceViewDocument):
    pass
