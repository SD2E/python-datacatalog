from ..common import MongoAggregation, MongoViewDocument

class JobsViewDocument(MongoViewDocument):
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(JobsViewDocument, self).__init__(
            inheritance=inheritance, **kwargs)
        setattr(self, '_index', True)
        self.update_id()

class ViewDocumentInterface(JobsViewDocument):
    pass
