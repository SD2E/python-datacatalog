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
from ..basestore import CatalogUpdateFailure, HeritableDocumentSchema, LinkedStore, JSONSchemaCollection

class ExperimentUpdateFailure(CatalogUpdateFailure):
    pass

class ExperimentDocument(HeritableDocumentSchema):
    """Defines a completed instance of an experimental design"""

    def __init__(self, inheritance=True, **kwargs):
        super(ExperimentDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class ExperimentStore(LinkedStore):
    """Manage storage and retrieval of ExperimentDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ExperimentStore, self).__init__(mongodb, config, session)
        schema = ExperimentDocument(**kwargs)
        super(ExperimentStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(ExperimentStore):
    pass
