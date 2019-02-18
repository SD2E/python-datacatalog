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
from ..basestore import LinkedStore
from ..basestore import HeritableDocumentSchema, JSONSchemaCollection, formatChecker
from ..basestore import CatalogUpdateFailure
from ...pathmappings import normalize, abspath, relativize, normpath
from ...filetypes import infer_filetype

class ReferenceUpdateFailure(CatalogUpdateFailure):
    pass

class ReferenceDocument(HeritableDocumentSchema):
    """Defines metadata for a Reference Entity"""

    def __init__(self, inheritance=True, **kwargs):
        super(ReferenceDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class ReferenceRecord(collections.UserDict):
    """New document for ReferenceStore with schema enforcement"""

    def __init__(self, value, *args, **kwargs):
        # if 'file_id' not in value:
        #     value['file_id'] = 'file.tacc.' + uuid.uuid1().hex
        value = dict(value)
        self.schema = ReferenceDocument()
        for k in self.schema.filter_keys():
            try:
                del value[k]
            except KeyError:
                pass

        jsonschema.validate(value, self.schema.to_dict(),
                            format_checker=formatChecker())
        super().__init__(value, *args, **kwargs)


class ReferenceStore(LinkedStore):
    """Manage storage and retrieval of ReferenceDocument records"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ReferenceStore, self).__init__(mongodb, config, session)
        schema = ReferenceDocument(**kwargs)
        super(ReferenceStore, self).update_attrs(schema)
        self.setup()

    def add_update_document(self, document_dict, uuid=None, token=None, strategy='merge'):
        if 'reference_id' not in document_dict:
            suggested_id = encode_name(document_dict['name'])
            raise KeyError("Reference document must have a 'reference_id'. " +
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

class StoreInterface(ReferenceStore):
    pass

def encode_name(textstring, separator='_', stopwords=[], case_insensitive=False):
    return separator.join(slug for slug in slugify(
        textstring, stopwords=stopwords,
        lowercase=case_insensitive).split('-'))
