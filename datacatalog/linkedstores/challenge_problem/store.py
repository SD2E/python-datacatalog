import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, JSONSchemaCollection, linkages
DEFAULT_LINK_FIELDS = list()

class ChallengeUpdateFailure(CatalogUpdateFailure):
    pass

class ChallengeDocument(HeritableDocumentSchema):
    """Defines a challenge problem or broad research topic"""

    def __init__(self, inheritance=True, **kwargs):
        super(ChallengeDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class ChallengeStore(LinkedStore):
    """Manage storage and retrieval of ChallengeDocuments"""
    LINK_FIELDS = DEFAULT_LINK_FIELDS

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ChallengeStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = ChallengeDocument(**kwargs)
        super(ChallengeStore, self).update_attrs(schema)
        self.setup()
        # sys.exit(0)

class StoreInterface(ChallengeStore):
    pass
