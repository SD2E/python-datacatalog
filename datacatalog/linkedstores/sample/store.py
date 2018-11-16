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
from ..basestore import BaseStore, CatalogUpdateFailure, HeritableDocumentSchema

class SampleUpdateFailure(CatalogUpdateFailure):
    pass

class SampleDocument(HeritableDocumentSchema):
    """Defines one of the samples in an experiment"""

    def __init__(self, inheritance=True, **kwargs):
        super(SampleDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class SampleStore(BaseStore):
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        """Manage storage and retrieval of SampleDocuments"""
        super(SampleStore, self).__init__(mongodb, config, session)
        schema = SampleDocument(**kwargs)
        super(SampleStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(SampleStore):
    pass
