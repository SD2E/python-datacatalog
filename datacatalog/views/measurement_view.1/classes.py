from ..common import MongoAggregation, MongoViewDocument

class MeasurementViewDocument(MongoViewDocument):
    """Represents a document from the experiment_design view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(MeasurementViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(MeasurementViewDocument):
    """Generic interface to ExperimentDesignViewDocument"""
    pass
