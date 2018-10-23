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

from dicthelpers import data_merge
from pathmappings import normalize, abspath
from pprint import pprint

from ..basestore import BaseStore, CatalogUpdateFailure, DocumentSchema, HeritableDocumentSchema, SoftDelete, time_stamp, msec_precision
from .schema import PipelineDocument
from .serializer import SerializedPipeline
from .exceptions import PipelineUpdateFailure, DuplicatePipelineError, PipelineUpdateFailure

class PipelineStore(SoftDelete, BaseStore):
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(PipelineStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = PipelineDocument(**kwargs)
        setattr(self, 'name', schema.get_collection())
        setattr(self, 'schema', schema.to_dict())
        setattr(self, 'identifiers', schema.get_identifiers())
        setattr(self, 'uuid_type', schema.get_uuid_type())
        setattr(self, 'uuid_field', schema.get_uuid_field())
        self.setup()

    def get_typed_uuid(self, components_list, binary=False):
        sp = SerializedPipeline(components_list)
        return super(PipelineStore, self).get_typed_uuid(sp.to_json(), binary=binary)
