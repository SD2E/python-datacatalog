from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, JSONSchemaCollection
from ...pathmappings import normalize, abspath, relativize, normpath

class FileUpdateFailure(CatalogUpdateFailure):
    pass

class FileDocument(HeritableDocumentSchema):
    """Defines experiment-linked metadata for a file"""

    def __init__(self, inheritance=True, **kwargs):
        super(FileDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


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
                                           uuid, token,
                                           strategy)

    def get_typeduuid(self, payload, binary=False):
        identifier_string = None
        if isinstance(payload, dict):
            if 'name' in payload:
                payload['name'] = normpath(payload['name'])
            identifier_string = self.get_linearized_values(payload)
        else:
            identifier_string = normpath(str(payload))
        return super().get_typeduuid(identifier_string, binary)

class StoreInterface(FileStore):
    pass
