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
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema

class MeasurementUpdateFailure(CatalogUpdateFailure):
    pass

class MeasurementDocument(HeritableDocumentSchema):
    """Defines a measurement in a sample"""

    def __init__(self, inheritance=True, **kwargs):
        super(MeasurementDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class MeasurementStore(LinkedStore):
    """Manage storage and retrieval of MeasurementDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(MeasurementStore, self).__init__(mongodb, config, session)
        schema = MeasurementDocument(**kwargs)
        super(MeasurementStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(MeasurementStore):
    """Generic interface to MeasurementStore"""
    pass
