import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ...identifiers.typeduuid import catalog_uuid
from ...extensible import ExtensibleAttrDict
from ...utils import time_stamp, msec_precision
from ..basestore import HeritableDocumentSchema

TYPE_SIGNATURE = ('inline_annotation', '119', 'Inline annotation')

class InlineAnnotationSchema(HeritableDocumentSchema):
    """Defines the inline annotation schema"""

    def __init__(self, data=None):
        super(InlineAnnotationSchema, self).__init__(
            inheritance=True,
            document='inline_annotation.json',
            filters='inline_annotation_filters.json')
        self.update_id()

class InlineAnnotationDocument(ExtensibleAttrDict):
    """Instantiates an instance of inline annotation"""

    PARAMS = [('uuid', False, 'uuid', None),
              ('date', False, 'date', None),
              ('data', False, 'data', 'Empty annotation')]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = InlineAnnotationSchema()
        for attr, req, param, default in self.PARAMS:
            setattr(self, attr, kwargs.get(param, default))
        self.name = 'annotation'
        if self.date is None:
            setattr(self, 'date', msec_precision(time_stamp()))
        self.uuid = catalog_uuid(
            str(self.data) + self.date.isoformat(),
            schema.get_uuid_type())

class InlineAnnotationStore(object):
    pass
