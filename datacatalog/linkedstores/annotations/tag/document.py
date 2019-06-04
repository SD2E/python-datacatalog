import inspect
import json
import os
import re
import sys
import validators

from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.identifiers.typeduuid import catalog_uuid, get_uuidtype
from datacatalog.identifiers import tacc
from datacatalog.linkedstores.basestore import HeritableDocumentSchema

TYPE_SIGNATURE = ('tag_annotation', '122', 'Tag Annotation')
TAG_NAME_REGEX = re.compile('^[a-zA-Z0-9][a-zA-Z0-9-.]{1,62}[a-zA-Z0-9]$')
TAG_DESC_MAX_LEN = 256

class TagAnnotationSchema(HeritableDocumentSchema):
    """Defines the Tag Annotation schema"""

    def __init__(self, inheritance=True, **kwargs):
        super(TagAnnotationSchema, self).__init__(
            inheritance=True,
            document='schema.json',
            filters='filters.json',
            **kwargs)
        self.update_id()

class TagAnnotationDocument(ExtensibleAttrDict):
    """Instantiates an instance of Tag Annotation"""

    PARAMS = [('name', True, 'name', 'generic.tag'),
              ('description', False, 'description', ''),
              ('owner', True, 'owner', 'public'),
              ('_visible', False, '_visible', True)]

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
        # Validate value for name
        if not TAG_NAME_REGEX.search(self.name):
            raise ValueError('{} is not a valid tag name'.format(self.name))
        # Enforce max description length
        if len(self.description) > 255:
            raise ValueError(
                'Tag description can have a max of {} characters'.format(
                    TAG_DESC_MAX_LEN))
