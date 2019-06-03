import inspect
import json
import os
import sys
from pprint import pprint

from datacatalog import linkages
from datacatalog.dicthelpers import data_merge
from datacatalog.identifiers.typeduuid import get_uuidtype
from datacatalog.linkedstores.basestore import (
    LinkedStore, CatalogUpdateFailure, SoftDelete,
    JSONSchemaCollection)
from .document import TextAnnotationSchema, TYPE_SIGNATURE
from ..exceptions import AnnotationError

class TextAnnotationStore(SoftDelete, LinkedStore):
    """Manage storage and retrieval of TagAnnotation documents"""
    LINK_FIELDS = [linkages.CHILD_OF]

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(TextAnnotationStore, self).__init__(mongodb, config, session)
        schema = TextAnnotationSchema(**kwargs)
        super(TextAnnotationStore, self).update_attrs(schema)
        self._enforce_auth = True
        self.setup(update_indexes=kwargs.get('update_indexes', False))

    def reply(self, parent_uuid, document_dict, token=None):
        """Automatically links a text annotation to its parent
        """

        if get_uuidtype(parent_uuid) != TYPE_SIGNATURE[0]:
            raise AnnotationError('UUID was the wrong type for reply()')
        if self.find_one_by_uuid(parent_uuid) is None:
            raise AnnotationError('Parent document does not exist')

        document_dict[linkages.CHILD_OF] = [parent_uuid]
        return self.add_document(document_dict, token=token)


class StoreInterface(TextAnnotationStore):
    pass
