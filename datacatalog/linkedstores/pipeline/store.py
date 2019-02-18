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
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, SoftDelete

from .schema import PipelineDocument
from .serializer import SerializedPipeline
from .exceptions import PipelineCreateFailure, PipelineUpdateFailure, DuplicatePipelineError

class PipelineStore(SoftDelete, LinkedStore):
    """Manage storage and retrieval of PipelineDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(PipelineStore, self).__init__(mongodb, config, session)
        schema = PipelineDocument(**kwargs)
        super(PipelineStore, self).update_attrs(schema)
        self._enforce_auth = False
        self.setup()

    # TODO: Figure out how to patch in Pipeline.id
    def get_typeduuid(self, payload, binary=False):
        """Pipelines-specific method for getting a UUID

        Args:
            payload (object): A list or dict containing the pipeline definition

        Returns:
            str: A UUID for this Pipeline
        """
        # print('PAYLOAD', payload)
        uuid_els = list()
        uuid_els.append(payload.get('id', 'pipeline.id'))

        cplist = payload.get('components', [])
        spdoc = SerializedPipeline(cplist).to_json()
        uuid_els.append(spdoc)
        uuid_target = ':'.join(uuid_els)
        # print('UUID_TARGET', uuid_target)
        return super(PipelineStore, self).get_typeduuid(uuid_target, binary=binary)

class StoreInterface(PipelineStore):
    pass
