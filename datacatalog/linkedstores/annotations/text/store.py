import inspect
import json
import os
import sys
from pprint import pprint

from datacatalog import linkages
from datacatalog.dicthelpers import data_merge
from datacatalog.linkedstores.basestore import (
    LinkedStore, CatalogUpdateFailure, SoftDelete,
    JSONSchemaCollection)
from .document import TextAnnotationSchema
from ..exceptions import AnnotationError

class TextAnnotationStore(SoftDelete, LinkedStore):
    """Manage storage and retrieval of TagAnnotation documents"""
    LINK_FIELDS = [linkages.CHILD_OF]

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(TextAnnotationStore, self).__init__(mongodb, config, session)
        schema = TextAnnotationSchema(**kwargs)
        super(TextAnnotationStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))

class StoreInterface(TextAnnotationStore):
    pass
