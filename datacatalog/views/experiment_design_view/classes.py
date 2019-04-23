from ..common import MongoAggregation, MongoViewDocument

class ChallengeProblemViewDocument(MongoViewDocument):
    """Represents a document from the challenge_problem_experiment_design view"""
    _index = False

    def __init__(self, inheritance=False, **kwargs):
        super(ChallengeProblemViewDocument, self).__init__(inheritance=inheritance, **kwargs)
        self.set_indexable(True)
        self.update_id()

class ViewDocumentInterface(ChallengeProblemViewDocument):
    """Generic interface to ChallengeProblemViewDocument"""
    pass
