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

class ExperimentDesignUpdateFailure(CatalogUpdateFailure):
    pass

class ExperimentDesignDocument(HeritableDocumentSchema):
    """Defines a an experimental design with optional link to external URI"""

    def __init__(self, inheritance=True, **kwargs):
        super(ExperimentDesignDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class ExperimentDesignStore(LinkedStore):
    """Manage storage and retrieval of ExperimentDesignDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ExperimentDesignStore, self).__init__(mongodb, config, session)
        schema = ExperimentDesignDocument(**kwargs)
        super(ExperimentDesignStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(ExperimentDesignStore):
    pass
