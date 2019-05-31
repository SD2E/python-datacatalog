import inspect
import json
import os
import sys
from pprint import pprint

from datacatalog.dicthelpers import data_merge
from datacatalog.linkedstores.basestore import (
    LinkedStore, CatalogUpdateFailure, JSONSchemaCollection)
from .document import TextAnnotationSchema

class AnnotationUpdateFailure(CatalogUpdateFailure):
    pass

class TextAnnotationStore(LinkedStore):
    """Manage storage and retrieval of TagAnnotation documents"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(TextAnnotationStore, self).__init__(mongodb, config, session)
        schema = TextAnnotationSchema(**kwargs)
        super(TextAnnotationStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))

class StoreInterface(TextAnnotationStore):
    pass
