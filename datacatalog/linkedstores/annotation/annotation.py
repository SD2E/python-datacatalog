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

TYPE_SIGNATURE = ('annotation', '118', 'Annotation')

class AnnotationSchema(HeritableDocumentSchema):
    """Defines the inline annotation schema"""

    def __init__(self, inheritance=True, **kwargs):
        super(AnnotationSchema, self).__init__(
            inheritance=True,
            document='annotation.json',
            filters='annotation_filters.json',
            **kwargs)
        self.update_id()

class AnnotationDocument(ExtensibleAttrDict):
    """Instantiates an instance of inline annotation"""

    PARAMS = [('uuid', False, 'uuid', None),
              ('date', False, 'date', None),
              ('data', False, 'data', 'Empty annotation')]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = AnnotationSchema()
        for attr, req, param, default in self.PARAMS:
            setattr(self, attr, kwargs.get(param, default))
        self.name = 'annotation'
        if self.date is None:
            setattr(self, 'date', msec_precision(time_stamp()))
        self.uuid = catalog_uuid(
            str(self.data) + self.date.isoformat(),
            schema.get_uuid_type())


