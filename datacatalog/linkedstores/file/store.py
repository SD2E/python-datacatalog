from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import collections
import inspect
import json
import jsonschema
import os
import sys
import uuid
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import LinkedStore
from ..basestore import HeritableDocumentSchema, JSONSchemaCollection, formatChecker
from ..basestore import CatalogUpdateFailure
from ...pathmappings import normalize, abspath, relativize, normpath
from ...filetypes import infer_filetype

DEFAULT_LINK_FIELDS = ('child_of', 'derived_from', 'generated_by', 'derived_using')
class FileUpdateFailure(CatalogUpdateFailure):
    pass

class FileDocument(HeritableDocumentSchema):
    """Defines experiment-linked metadata for a file"""

    def __init__(self, inheritance=True, **kwargs):
        super(FileDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class FileRecord(collections.UserDict):
    """New document for FileStore with schema enforcement"""

    def __init__(self, value, *args, **kwargs):
        # if 'file_id' not in value:
        #     value['file_id'] = 'file.tacc.' + uuid.uuid1().hex
        value = dict(value)
        self.schema = FileDocument()
        for k in self.schema.filter_keys():
            try:
                del value[k]
            except KeyError:
                pass

        jsonschema.validate(value, self.schema.to_dict(),
                            format_checker=formatChecker())
        super().__init__(value, *args, **kwargs)


class FileStore(LinkedStore):
    """Manage storage and retrieval of FileDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(FileStore, self).__init__(mongodb, config, session)
        schema = FileDocument(**kwargs)
        super(FileStore, self).update_attrs(schema)
        self.setup()

    def add_update_document(self, document_dict, uuid=None, token=None, strategy='merge'):
        if 'name' in document_dict:
            document_dict['name'] = normpath(document_dict['name'])
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

class StoreInterface(FileStore):
    pass
