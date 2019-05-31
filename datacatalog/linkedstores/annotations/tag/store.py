import inspect
import json
import os
import sys
from pprint import pprint

from datacatalog.dicthelpers import data_merge
from datacatalog.linkedstores.basestore import (
    LinkedStore, CatalogUpdateFailure, JSONSchemaCollection)
from .document import TagAnnotationSchema

class AnnotationUpdateFailure(CatalogUpdateFailure):
    pass

class TagAnnotationStore(LinkedStore):
    """Manage storage and retrieval of TagAnnotation documents"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(TagAnnotationStore, self).__init__(mongodb, config, session)
        schema = TagAnnotationSchema(**kwargs)
        super(TagAnnotationStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))

class StoreInterface(TagAnnotationStore):
    pass
