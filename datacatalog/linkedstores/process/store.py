import collections
import inspect
import json
import jsonschema
import os
import sys
import uuid
from pprint import pprint
from slugify import slugify

from ...dicthelpers import data_merge
from ..basestore import LinkedStore, linkages
from ..basestore import HeritableDocumentSchema, JSONSchemaCollection, formatChecker
from ..basestore import CatalogUpdateFailure
from ...stores import abspath
from ...utils import normalize, normpath
from ...filetypes import infer_filetype

class ProcessUpdateFailure(CatalogUpdateFailure):
    pass

class ProcessDocument(HeritableDocumentSchema):
    """Defines metadata for a Process Entity"""

    def __init__(self, inheritance=True, **kwargs):
        super(ProcessDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class ProcessRecord(collections.UserDict):
    """New document for ProcessStore with schema enforcement"""
    LINK_FIELDS = [linkages.CHILD_OF, linkages.DERIVED_FROM]

    def __init__(self, value, *args, **kwargs):
        # if 'file_id' not in value:
        #     value['file_id'] = 'file.tacc.' + uuid.uuid1().hex
        value = dict(value)
        self.schema = ProcessDocument()
        for k in self.schema.filter_keys():
            try:
                del value[k]
            except KeyError:
                pass

        jsonschema.validate(value, self.schema.to_dict(),
                            format_checker=formatChecker())
        super().__init__(value, *args, **kwargs)


class ProcessStore(LinkedStore):
    """Manage storage and retrieval of ProcessDocument records"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ProcessStore, self).__init__(mongodb, config, session)
        schema = ProcessDocument(**kwargs)
        super(ProcessStore, self).update_attrs(schema)
        self.setup()

    def add_update_document(self, document_dict, uuid=None, token=None, strategy='merge'):
        if 'process_id' not in document_dict:
            suggested_id = encode_name(document_dict['name'])
            raise KeyError("Process document must have a 'processe_id'. " +
                           "Based on the provided name, here is a suggestion: {}".format(suggested_id))
        return super().add_update_document(document_dict,
                                           uuid=uuid, token=token,
                                           strategy=strategy)

    def get_typeduuid(self, payload, binary=False):
        identifier_string = None
        if isinstance(payload, dict):
            if 'name' in payload:
                payload['name'] = normpath(payload['name'])
            identifier_string = self.get_linearized_values(payload)
        else:
            identifier_string = normpath(str(payload))
        # print('IDENTIFIER.string', identifier_string)
        return super().get_typeduuid(identifier_string, binary)

class StoreInterface(ProcessStore):
    pass

def encode_name(textstring, separator='_', stopwords=[], case_insensitive=False):
    return separator.join(slug for slug in slugify(
        textstring, stopwords=stopwords,
        lowercase=case_insensitive).split('-'))
