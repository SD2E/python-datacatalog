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

TYPE_SIGNATURE = ('tag_annotation', '122', 'Tag Annotation')

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

    PARAMS = [('name', False, 'value', None),
              ('description', False, 'description', None)]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = TagAnnotationSchema()
        for attr, req, param, default in self.PARAMS:
            setattr(self, attr, kwargs.get(param, default))
        # self.uuid = catalog_uuid(
        #     str(self.value) + self.created.isoformat(),
        #     schema.get_uuid_type())

