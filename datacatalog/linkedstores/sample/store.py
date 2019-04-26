import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, JSONSchemaCollection, linkages
DEFAULT_LINK_FIELDS = [linkages.CHILD_OF]

class SampleUpdateFailure(CatalogUpdateFailure):
    pass

class SampleDocument(HeritableDocumentSchema):
    """Defines one of the samples in an experiment"""

    def __init__(self, inheritance=True, **kwargs):
        super(SampleDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class SampleStore(LinkedStore):

    LINK_FIELDS = DEFAULT_LINK_FIELDS

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        """Manage storage and retrieval of SampleDocuments"""
        super(SampleStore, self).__init__(mongodb, config, session)
        schema = SampleDocument(**kwargs)
        super(SampleStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))

class StoreInterface(SampleStore):
    pass
