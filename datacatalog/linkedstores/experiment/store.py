import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import CatalogUpdateFailure, HeritableDocumentSchema, LinkedStore, JSONSchemaCollection, linkages
DEFAULT_LINK_FIELDS = [linkages.CHILD_OF]

class ExperimentUpdateFailure(CatalogUpdateFailure):
    pass

class ExperimentDocument(HeritableDocumentSchema):
    """Defines a completed instance of an experimental design"""

    def __init__(self, inheritance=True, **kwargs):
        super(ExperimentDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class ExperimentStore(LinkedStore):
    """Manage storage and retrieval of ExperimentDocuments"""
    LINK_FIELDS = DEFAULT_LINK_FIELDS

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ExperimentStore, self).__init__(mongodb, config, session)
        schema = ExperimentDocument(**kwargs)
        super(ExperimentStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(ExperimentStore):
    pass
