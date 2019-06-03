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
from .document import (TextAnnotationDocument,
                       TextAnnotationSchema,
                       TYPE_SIGNATURE)
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

    def new_text(self, subject, body=None, owner=None, token=None):
        """Create a new TextAnnotation record
        """
        doc_dict = TextAnnotationDocument(subject=subject,
                                          body=body,
                                          owner=owner)
        return self.add_update_document(doc_dict)

    def new_reply(self, parent_text_uuid, subject,
                  body=None, owner=None, token=None):
        """Automatically create and link a TextAnnotation to its parent
        """

        if get_uuidtype(parent_text_uuid) != TYPE_SIGNATURE[0]:
            raise AnnotationError('UUID was the wrong type for new_reply()')
        if self.find_one_by_uuid(parent_text_uuid) is None:
            raise AnnotationError('Parent TextAnnotation does not exist')

        doc_dict = TextAnnotationDocument(subject=subject,
                                          body=body,
                                          owner=owner)
        doc_dict[linkages.CHILD_OF] = [parent_text_uuid]
        return self.add_document(doc_dict, token=token)


class StoreInterface(TextAnnotationStore):
    pass
