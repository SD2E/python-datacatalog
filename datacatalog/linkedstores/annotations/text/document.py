import inspect
import json
import os
import sys
import validators

from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.identifiers import tacc
from datacatalog.identifiers.typeduuid import catalog_uuid, get_uuidtype
from datacatalog.linkedstores.basestore import HeritableDocumentSchema

TYPE_SIGNATURE = ('text_annotation', '123', 'Text Annotation')
TEXT_SUBJECT_MAX_LENGTH = 256
TEXT_BODY_MAX_LENGTH = 2048

class TextAnnotationSchema(HeritableDocumentSchema):
    """Defines the Tag Annotation schema"""

    def __init__(self, inheritance=True, **kwargs):
        super(TextAnnotationSchema, self).__init__(
            inheritance=True,
            document='schema.json',
            filters='filters.json',
            **kwargs)
        self.update_id()

class TextAnnotationDocument(ExtensibleAttrDict):
    """Instantiates an instance of Tag Annotation"""

    PARAMS = [('body', True, 'body', None),
              ('subject', False, 'subject', ''),
              ('owner', True, 'owner', None),
              ('_visible', False, '_visible', True)]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = TextAnnotationSchema()
        for attr, req, param, default in self.PARAMS:
            if req is True:
                if attr not in kwargs:
                    raise KeyError('{} is a mandatory field'.format(attr))
            setattr(self, attr, kwargs.get(param, default))

        # TACC username or email (lexical check)
        if not tacc.username.validate(self.owner, permissive=True):
            if not validators.email(self.owner):
                raise ValueError('Owner must be a TACC username or valid email')
        # Validate body and subject length
        if len(str(self.body)) > TEXT_BODY_MAX_LENGTH:
            raise ValueError(
                'Body cannot be more than {} characters'.format(
                    TEXT_BODY_MAX_LENGTH))
        if len(str(self.subject)) > TEXT_SUBJECT_MAX_LENGTH:
            raise ValueError(
                'Subject cannot be more than {} characters'.format(
                    TEXT_SUBJECT_MAX_LENGTH))

        # Create a child_of linkage. We do this rather than use an Association
        # because its logically more simple for end users to query and
        # because MOST of the datacatalog schema works this way
        child_of = kwargs.get('child_of', list())
        if isinstance(child_of, str):
            child_of = [child_of]
        for co in child_of:
            if get_uuidtype(co) != TYPE_SIGNATURE[0]:
                raise ValueError(
                    'Can only be a child_of {}'.format(TYPE_SIGNATURE[2]))
        self.child_of = child_of
