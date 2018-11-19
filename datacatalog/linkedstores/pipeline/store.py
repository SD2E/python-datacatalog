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
from ...pathmappings import normalize, abspath
from ..basestore import BaseStore, CatalogUpdateFailure, HeritableDocumentSchema, SoftDelete

from .schema import PipelineDocument
from .serializer import SerializedPipeline
from .exceptions import PipelineCreateFailure, PipelineUpdateFailure, DuplicatePipelineError

class PipelineStore(SoftDelete, BaseStore):
    """Manage storage and retrieval of PipelineDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(PipelineStore, self).__init__(mongodb, config, session)
        schema = PipelineDocument(**kwargs)
        super(PipelineStore, self).update_attrs(schema)
        self.setup()

    def get_typed_uuid(self, payload, binary=False):
        cplist = payload.get('components', [])
        spdoc = SerializedPipeline(cplist).to_json()
        return super(PipelineStore, self).get_typed_uuid(spdoc, binary=binary)

class StoreInterface(PipelineStore):
    pass
