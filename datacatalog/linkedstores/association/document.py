import inspect
import json
import os
import sys

from attrdict import AttrDict
from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.identifiers.typeduuid import catalog_uuid, get_uuidtype
from datacatalog.identifiers import tacc
from datacatalog.linkedstores.basestore import HeritableDocumentSchema
from datacatalog.settings import MONGO_DELETE_FIELD

TYPE_SIGNATURE = ('association', '124', 'Association')

class AssociationSchema(HeritableDocumentSchema):
    """Defines the Annotation Association schema"""
    DELETE_FIELD = MONGO_DELETE_FIELD

    def __init__(self, inheritance=True, **kwargs):
        super(AssociationSchema, self).__init__(
            inheritance=True,
            document='schema.json',
            filters='filters.json',
            **kwargs)
        self.update_id()

class AssociationDocument(ExtensibleAttrDict):
    """Instantiates an Annotation Association"""

    DELETE_FIELD = MONGO_DELETE_FIELD
    PARAMS = [('owner', True, 'owner', None),
              ('connects_to', True, 'connects_to', []),
              ('connects_from', True, 'connects_from', []),
              ('note', False, 'note', None),
              (DELETE_FIELD, False, DELETE_FIELD, True)]

    CONNECTS_TO_UUIDTYPES = (
        'challenge_problem', 'experiment_design',
        'experiment', 'sample', 'measurement', 'file',
        'reference', 'process',
        'pipeline', 'pipelinejob')
    CONNECTS_TO_MAX_LENGTH = 1

    CONNECTS_FROM_UUIDTYPES = ('tag_annotation', 'text_annotation')
    CONNECTS_FROM_MAX_LENGTH = 1

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = AssociationSchema()
        for attr, req, param, default in self.PARAMS:
            if req is True:
                if attr not in kwargs:
                    raise KeyError('{} is a mandatory field'.format(attr))
            setattr(self, attr, kwargs.get(param, default))

        # Lexically check username
        tacc.username.validate(self.owner, permissive=False)

        # Cast to list context for forward compatibility with multiple values
        for attr in ['connects_to', 'connects_from']:
            val = getattr(self, attr)
            if not isinstance(val, list):
                val = [val]
            setattr(self, attr, val)

        # Check length of connects_* lists
        if len(getattr(self, 'connects_to')) > self.CONNECTS_TO_MAX_LENGTH:
            raise ValueError(\
                'connects_to may hold {} value(s)'.format(
                    self.CONNECTS_TO_MAX_LENGTH))
        if len(getattr(self, 'connects_from')) > self.CONNECTS_FROM_MAX_LENGTH:
            raise ValueError(
                'connects_from may hold {} value(s)'.format(
                    self.CONNECTS_FROM_MAX_LENGTH))

        # Validate onnects_from contains refs to AnnotationDoc type
        for u in getattr(self, 'connects_from'):
            if get_uuidtype(u) not in self.CONNECTS_FROM_UUIDTYPES:
                raise ValueError(
                    'typeduuid {} is invalid for connects_from'.format(u))
        # Validate onnects_to contains refs to any allowed type
        for u in getattr(self, 'connects_to'):
            if get_uuidtype(u) not in self.CONNECTS_TO_UUIDTYPES:
                raise ValueError(
                    'typeduuid {} is invalid for connects_to'.format(u))

class Association(AttrDict):
    pass
