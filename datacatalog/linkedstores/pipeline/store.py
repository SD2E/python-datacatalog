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
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(PipelineStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = PipelineDocument(**kwargs)
        super(PipelineStore, self).update_attrs(schema)
        # setattr(self, 'name', schema.get_collection())
        # setattr(self, 'schema', schema.to_dict())
        # setattr(self, 'identifiers', schema.get_identifiers())
        # setattr(self, 'uuid_type', schema.get_uuid_type())
        # setattr(self, 'uuid_fields', schema.get_uuid_fields())
        self.setup()

    def get_typed_uuid(self, payload, binary=False):
        cplist = payload.get('components', [])
        spdoc = SerializedPipeline(cplist).to_json()
        return super(PipelineStore, self).get_typed_uuid(spdoc, binary=binary)

class StoreInterface(PipelineStore):
    pass
