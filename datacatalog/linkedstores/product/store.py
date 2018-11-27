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

class ProductUpdateFailure(CatalogUpdateFailure):
    pass

class ProductDocument(HeritableDocumentSchema):
    """Defines experiment-linked metadata for a file"""

    def __init__(self, inheritance=True, **kwargs):
        super(ProductDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class ProductStore(LinkedStore):
    """Manage storage and retrieval of ProductDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(FileStore, self).__init__(mongodb, config, session)
        schema = ProductDocument(**kwargs)
        super(ProductStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(ProductStore):
    pass
