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

from ..basestore import BaseStore, CatalogUpdateFailure, DocumentSchema, HeritableDocumentSchema, time_stamp
from dicthelpers import data_merge
from pprint import pprint

class ExperimentUpdateFailure(CatalogUpdateFailure):
    pass

class ExperimentDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=True, **kwargs):
        super(ExperimentDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class ExperimentStore(BaseStore):
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ExperimentStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = ExperimentDocument(**kwargs)
        setattr(self, 'name', schema.get_collection())
        setattr(self, 'schema', schema.to_dict())
        setattr(self, 'identifiers', schema.get_identifiers())
        setattr(self, 'uuid_type', schema.get_uuid_type())
        self.setup()
