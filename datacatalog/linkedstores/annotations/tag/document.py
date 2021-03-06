import inspect
import json
import os
import re
import sys
import validators

from attrdict import AttrDict
from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.identifiers.typeduuid import catalog_uuid, get_uuidtype
from datacatalog.identifiers import tacc
from datacatalog.linkedstores.basestore import HeritableDocumentSchema
from datacatalog.settings import MONGO_DELETE_FIELD

TYPE_SIGNATURE = ('tag_annotation', '122', 'Tag Annotation')

TAG_NAME_MAX_LEN = 64
TAG_NAME_REGEX = re.compile('^[a-zA-Z0-9][a-zA-Z0-9-.]{1,62}[a-zA-Z0-9]$')
TAG_DESC_MAX_LEN = 256
TAG_DESC_REGEX = re.compile('^.{0,256}$')

class TagAnnotationSchema(HeritableDocumentSchema):
    """Defines the Tag Annotation schema"""
    DELETE_FIELD = MONGO_DELETE_FIELD

    def __init__(self, inheritance=True, **kwargs):
        super(TagAnnotationSchema, self).__init__(
            inheritance=True,
            document='schema.json',
            filters='filters.json',
            **kwargs)
        self.update_id()

class TagAnnotationDocument(ExtensibleAttrDict):
    """Instantiates an instance of Tag Annotation"""

    DELETE_FIELD = MONGO_DELETE_FIELD
    PARAMS = [('name', True, 'name', 'generic.tag'),
              ('description', False, 'description', ''),
              ('owner', True, 'owner', 'public'),
              (DELETE_FIELD, False, DELETE_FIELD, True)]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = TagAnnotationSchema()
        for attr, req, param, default in self.PARAMS:
            if req is True:
                if attr not in kwargs:
                    raise KeyError('{} is a mandatory field'.format(attr))
            setattr(self, attr, kwargs.get(param, default))

        # TACC username or email (lexical check)
        if not tacc.username.validate(self.owner, permissive=True):
            if not validators.email(self.owner):
                raise ValueError('Owner must be a TACC username or valid email')

        # Tag length (technically redundant with regex validation)
        if len(self.name) >= TAG_NAME_MAX_LEN:
            raise ValueError(
                'Tag name can have a max of {} characters'.format(
                    TAG_NAME_MAX_LEN))
        # Validate name with regex
        if not TAG_NAME_REGEX.search(self.name):
            raise ValueError('{} is not a valid tag name'.format(self.name))
        # Max description length (technically redundant with regex validation)
        if len(self.description) > 255:
            raise ValueError(
                'Tag description can have a max of {} characters'.format(
                    TAG_DESC_MAX_LEN))
        # Validate description with regex
        if not TAG_DESC_REGEX.search(self.description):
            raise ValueError('This is not a valid tag description')

class TagAnnotation(AttrDict):
    pass
