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


class ChallengeUpdateFailure(CatalogUpdateFailure):
    pass

class ChallengeDocument(HeritableDocumentSchema):
    """Defines a challenge problem or broad research topic"""

    def __init__(self, inheritance=True, **kwargs):
        super(ChallengeDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class ChallengeStore(BaseStore):
    """Manage storage and retrieval of ChallengeDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(ChallengeStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = ChallengeDocument(**kwargs)
        super(ChallengeStore, self).update_attrs(schema)
        self.setup()

class StoreInterface(ChallengeStore):
    pass
