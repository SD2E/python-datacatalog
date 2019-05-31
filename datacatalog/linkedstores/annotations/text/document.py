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

TYPE_SIGNATURE = ('text_annotation', '123', 'Text Annotation')

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

    PARAMS = [('body', False, 'body', ''),
              ('subject', False, 'subject', ''),
              ('owner', False, 'owner', None)]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = TextAnnotationSchema()
        for attr, req, param, default in self.PARAMS:
            setattr(self, attr, kwargs.get(param, default))
        child_of = kwargs.get('child_of', list())
        if not isinstance(child_of, list):
            child_of = [child_of]
        self.child_of = child_of
        # self.uuid = catalog_uuid(
        #     str(self.value) + self.created.isoformat(),
        #     schema.get_uuid_type())

