import inspect
import json
import os
import sys
from pprint import pprint

from datacatalog.dicthelpers import data_merge
from datacatalog.linkedstores.basestore import (
    LinkedStore, AgaveClient, SoftDelete, CatalogUpdateFailure,
    JSONSchemaCollection, strategies)
from .document import TagAnnotationSchema, TagAnnotationDocument
from ..exceptions import AnnotationError

class TagAnnotationStore(SoftDelete, LinkedStore):
    """Manage storage and retrieval of TagAnnotation documents"""
    LINK_FIELDS = []

    def __init__(self, mongodb, config={}, session=None, agave=None, **kwargs):
        super(TagAnnotationStore, self).__init__(mongodb, config, session)
        schema = TagAnnotationSchema(**kwargs)
        super(TagAnnotationStore, self).update_attrs(schema)
        self._enforce_auth = True
        self.setup(update_indexes=kwargs.get('update_indexes', False))

    def new_tag(self, name, description=None, owner=None, token=None, **kwargs):
        doc = TagAnnotationDocument(name=name,
                                    description=description,
                                    owner=None,
                                    **kwargs)
        return self.add_update_document(doc, token=token)

class StoreInterface(TagAnnotationStore):
    pass
