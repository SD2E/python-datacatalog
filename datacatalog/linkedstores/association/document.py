import inspect
import json
import os
import sys

from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.identifiers.typeduuid import catalog_uuid, get_uuidtype
from datacatalog.identifiers import tacc
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
              ('connects_to', True, 'connects_to', []),
              ('connects_from', True, 'connects_from', []),
              ('_visible', False, '_visible', True)]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = AssociationSchema()
        for attr, req, param, default in self.PARAMS:
            if req is True:
                if attr not in kwargs:
                    raise KeyError('{} is a mandatory field'.format(attr))
            setattr(self, attr, kwargs.get(param, default))
        # TODO - Enforce types for at least connects_from. Code for this is up in AssociationStore
        for attr in ['connects_to', 'connects_from']:
            a = getattr(self, attr)
            if not isinstance(a, list):
                setattr(self, attr, [a])
        # Lexically check username
        tacc.username.validate(self.owner, permissive=False)
