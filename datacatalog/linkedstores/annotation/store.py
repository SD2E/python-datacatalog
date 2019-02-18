import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import LinkedStore, CatalogUpdateFailure, JSONSchemaCollection
from ..annotation import AnnotationSchema

class AnnotationUpdateFailure(CatalogUpdateFailure):
    pass

class AnnotationStore(LinkedStore):
    """Manage storage and retrieval of AnnotationDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(AnnotationStore, self).__init__(mongodb, config, session)
        schema = AnnotationSchema(**kwargs)
        super(AnnotationStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(AnnotationStore):
    pass
