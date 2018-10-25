from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object

import os
import sys
import inspect
import json

from pprint import pprint
from slugify import slugify
from jsonschemas import JSONSchemaBaseObject
from identifiers import typed_uuid
from utils import time_stamp, current_time, msec_precision

class DocumentSchema(JSONSchemaBaseObject):
    """Document interface for a JSON schema-informed document"""
    TYPED_UUID_TYPE = 'generic'
    TYPED_UUID_FIELD = ['id']
    DEFAULT_DOCUMENT_NAME = 'document.json'
    DEFAULT_FILTERS_NAME = 'filters.json'

    def __init__(self, **kwargs):
        doc_file = kwargs.get('document', self.DEFAULT_DOCUMENT_NAME)
        filt_file = kwargs.get('filters', self.DEFAULT_FILTERS_NAME)
        modfile = inspect.getfile(self.__class__)
        try:
            # Get default schema and filter documents from this base class
            class_schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
            class_filtersfile = os.path.join(os.path.dirname(__file__), self.DEFAULT_FILTERS_NAME)

            # Get instance schema and filter documents
            schemafile = os.path.join(os.path.dirname(modfile), doc_file)
            filtersfile = os.path.join(os.path.dirname(modfile), filt_file)

            if os.path.isfile(schemafile):
                schemaj = json.load(open(schemafile, 'r'))
            else:
                schemaj = json.load(open(class_schemafile, 'r'))

            if os.path.isfile(filtersfile):
                filtersj = json.load(open(filtersfile, 'r'))
            elif os.path.isfile(class_filtersfile):
                filtersj = json.load(open(class_filtersfile, 'r'))
            else:
                filtersj = dict()

            setattr(self, '_filters', filtersj)
        except Exception:
            schemaj = dict()

        params = {**schemaj, **kwargs}
        super(DocumentSchema, self).__init__(**params)
        # print(self.get_collection())
        self.update_id()

    def to_dict(self, private_prefix='_', document=False, **kwargs):
        my_dict = super(DocumentSchema, self).to_dict(private_prefix, **kwargs)
        filters = getattr(self, '_filters', {})
        filt_type = 'document'
        if document is False:
            filt_type = 'object'
        props_to_filter = filters.get(filt_type, {}).get('properties', [])
        resp_dict = dict()

        for k, v in my_dict.items():
            # Filter 'properties'
            if k == 'properties':
                filtered_props = dict()
                for pk, pv in v.items():
                    if pk not in props_to_filter:
                        filtered_props[pk] = pv
                v = filtered_props
            resp_dict[k] = v
            # Filter 'required'
            if k == 'required':
                for pk in props_to_filter:
                    try:
                        resp_dict['required'].remove(pk)
                    except ValueError:
                        pass
                    except Exception:
                        raise
        return resp_dict

    def get_identifiers(self):
        """Returns a list of top-level keys that are identifiers for this schema"""
        return getattr(self, '_identifiers', [])

    def get_indexes(self):
        """Returns the database indexes for this schema"""
        return getattr(self, '_indexes', [])

    def get_collection(self):
        """Returns the database collection that holds documents with this schema"""
        return getattr(self, '_collection', self.COLLECTION)

    def get_uuid_type(self):
        """Returns the TypedUUID type for documents in this schema"""
        return getattr(self, '_uuid_type', self.TYPED_UUID_TYPE)

    def get_uuid_fields(self):
        """Returns the document key that is used to assign a TypedUUID"""
        return getattr(self, '_uuid_fields', self.TYPED_UUID_FIELD)

    def get_typed_uuid(self, payload, binary=False):
        # print('TYPED_UUID_PAYLOAD: {}'.format(payload))
        if isinstance(payload, dict):
            identifier_string = self.get_serialized_document(payload)
        else:
            identifier_string = str(payload)
        new_uuid = typed_uuid.catalog_uuid(identifier_string, uuid_type=self.get_uuid_type(), binary=binary)
        # print('TYPED_UUID: {}'.format(new_uuid))
        return new_uuid

    def get_serialized_document(self, document, **kwargs):
        # Serialize values of specific keys to generate a UUID
        union = {**document, **kwargs}
        uuid_fields = self.get_uuid_fields()
        serialized = dict()
        for k in union:
            if k in uuid_fields:
                # print('TYPED_UUID_KEY: {}'.format(k))
                serialized[k] = union.get(k)
        serialized_document = json.dumps(serialized, indent=0, sort_keys=True, separators=(',', ':'))
        return serialized_document

    @classmethod
    def time_stamp(cls):
        return msec_precision(time_stamp())
