from ..common import MongoAggregation, MongoViewDocument

class ExperimentDesignViewDocument(MongoViewDocument):
    """Represents a document from the experiment_design view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(ExperimentDesignViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ExperimentDesignViewDocument):
    """Generic interface to ExperimentDesignViewDocument"""
    pass
