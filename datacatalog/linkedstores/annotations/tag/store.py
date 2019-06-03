import inspect
import json
import os
import sys
from pprint import pprint

from datacatalog.dicthelpers import data_merge
from datacatalog.linkedstores.basestore import (
    LinkedStore, AgaveClient, SoftDelete, CatalogUpdateFailure,
    JSONSchemaCollection, strategies)
from .document import TagAnnotationSchema
from ..exceptions import AnnotationError

class TagAnnotationStore(SoftDelete, LinkedStore):
    """Manage storage and retrieval of TagAnnotation documents"""
    LINK_FIELDS = []

    def __init__(self, mongodb, config={}, session=None, agave=None, **kwargs):
        super(TagAnnotationStore, self).__init__(mongodb, config, session)
        schema = TagAnnotationSchema(**kwargs)
        super(TagAnnotationStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))
        self._enforce_auth = True
        setattr(self, 'validate_owner', kwargs.get('validate_owner', False))

    def add_update_document(self, document_dict,
                            uuid=None, token=None, strategy='merge'):
        resp = super().add_update_document(document_dict,
                                           uuid=uuid, token=token,
                                           strategy=strategy)
        self.logger.info('add_update_document: {}'.format(resp))
        new_resp = resp
        return new_resp

class StoreInterface(TagAnnotationStore):
    pass
