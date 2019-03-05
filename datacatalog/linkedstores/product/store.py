import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import CatalogUpdateFailure, HeritableDocumentSchema, JSONSchemaCollection
from ..file import FileStore

class ProductUpdateFailure(CatalogUpdateFailure):
    pass

class ProductDocument(HeritableDocumentSchema):
    """Defines experiment-linked metadata for a file"""

    def __init__(self, inheritance=True, **kwargs):
        super(ProductDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class ProductStore(FileStore):
    """Manage storage and retrieval of ProductDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(FileStore, self).__init__(mongodb, config, session)
        schema = ProductDocument(**kwargs)
        super(ProductStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(ProductStore):
    pass
