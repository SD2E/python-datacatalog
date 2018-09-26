from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import binascii
import datetime
import filetype
import hashlib
import os

from pprint import pprint

from ..catalog import CatalogAttrDict
from ..identifiers.datacatalog_uuid import catalog_uuid
from ..utils import current_time, msec_precision
from .token import generate_salt
from .utils import components_to_pipeline, pipeline_to_uuid

class Pipeline(CatalogAttrDict):
    """Encapsulates the data model and business logic of a Pipeline"""
    # (param, create, update, attr/key, default)
    PARAMS = [
        ('_id', False, True, '_id', None),
        ('uuid', False, False, 'uuid', None),
        ('_uuid', False, False, '_uuid', None),
        ('_deleted', True, True, '_deleted', False),
        ('_salt', False, False, '_salt', None),
        ('pipeline_type', True, True, 'accepts', ['generic-process']),
        ('name', True, True, 'name', None),
        ('description', True, True, 'description', ''),
        ('components', True, False, 'components', []),
        ('properties', False, True, 'properties', {}),
        ('accepts', True, True, 'accepts', ['*']),
        ('produces', True, True, 'produces', ['*']),
        ('collections_levels', True, True, 'collections_levels', ['file']),
        ('processing_levels', True, True, 'processing_levels', ["0"]),
        ('child_of', False, False, 'child_of', [])]
    FILTERS = ['_salt', '_updated']

    def __init__(self, **kwargs):
        print('Pipeline.init()')
        for param, create, update, attr, default in self.PARAMS:
            try:
                # all params allowable on init
                if create:
                    value = kwargs.get(param, default)
                    setattr(self, attr, value)
            except KeyError:
                pass
        pprint(self)

    def create(self, **kwargs):
        print('Pipeline.create()')
        ts = msec_precision(current_time())
        for param, create, update, attr, default in self.PARAMS:
            try:
                if create:
                    value = kwargs.get(param, getattr(self, attr))
                    setattr(self, attr, value)
            except Exception:
                pass
        # to generate update token
        self._salt = generate_salt()
        # Generate UUID from component list
        doc = components_to_pipeline(self.components)
        self.uuid = pipeline_to_uuid(doc)
        self._uuid = pipeline_to_uuid(doc, binary=False)
        self.properties = {'created_date': ts, 'modified_date': ts, 'revision': 0}

    def update(self, **kwargs):
        ts = msec_precision(current_time())
        # # Load in from kwargs, which will be a database record
        # for param, create, update, attr, default in self.PARAMS:
        #     try:
        #         if update:
        #             value = kwargs.get(param, getattr(self, attr))
        #     except Exception:
        #         pass
        # setattr(self, attr, value)
        updated = False
        # Update attributes if present in content and allowed by PARAMS.update
        for param, create, update, attr, default in self.PARAMS:
            print(param)
            try:
                if update:
                    value = kwargs.get(param, getattr(self, attr))
                    if value != getattr(self, attr):
                        setattr(self, attr, value)
                        updated = True
            except Exception:
                pass

        # Update properties if we have evidence the record has changed
        if updated:
            self.properties['modified_date'] = ts
            self.properties['revision'] = self.properties['revision'] + 1

    def delete(self, force=False):
        self._deleted = True
        return self

    def undelete(self):
        self._deleted = False
        return self
