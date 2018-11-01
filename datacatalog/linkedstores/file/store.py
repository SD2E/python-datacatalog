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

from ..basestore import *
from dicthelpers import data_merge
from pprint import pprint

class FileUpdateFailure(CatalogUpdateFailure):
    pass

class FileDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=True, **kwargs):
        super(FileDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class FileStore(BaseStore):
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(FileStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = FileDocument(**kwargs)
        super(FileStore, self).update_attrs(schema)
        # setattr(self, 'name', schema.get_collection())
        # setattr(self, 'schema', schema.to_dict())
        # setattr(self, 'identifiers', schema.get_identifiers())
        # setattr(self, 'uuid_type', schema.get_uuid_type())
        # setattr(self, 'uuid_fields', schema.get_uuid_fields())
        self.setup()

class StoreInterface(FileStore):
    pass
