import inspect
import json
import os
import sys
from pprint import pprint

from datacatalog.dicthelpers import data_merge
from datacatalog.identifiers.typeduuid import catalog_uuid
from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.utils import time_stamp, msec_precision
from datacatalog.linkedstores.basestore import HeritableDocumentSchema

TYPE_SIGNATURE = ('association', '124', 'Association')

class AssociationSchema(HeritableDocumentSchema):
    """Defines the Annotation Association schema"""

    def __init__(self, inheritance=True, **kwargs):
        super(AssociationSchema, self).__init__(
            inheritance=True,
            document='schema.json',
            filters='filters.json',
            **kwargs)
        self.update_id()

class AssociationDocument(ExtensibleAttrDict):
    """Instantiates an Annotation Association"""

    PARAMS = [('owner', True, 'owner', None),
              ('connected_to', True, 'connected_to', []),
              ('connected_from', True, 'connected_from', []),
              ('_visible', False, '_visible', True)]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = AssociationSchema()
        for attr, req, param, default in self.PARAMS:
            setattr(self, attr, kwargs.get(param, default))

