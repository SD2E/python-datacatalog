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

from ..basestore import *
from .schema import FixityDocument
from .indexer import FixityIndexer
from .exceptions import FixtyUpdateFailure, FixityDuplicateError, FixtyNotFoundError


# FixityStore is a special case, as creates and manages its records as well as
# storing them. This is implemented in its index() method, which in turn
# instantiates a FixityIndexer. That object has sync() and render(), which
# capture the latest fixity data and render it into a JSON doc.

class FixityStore(BaseStore):
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(FixityStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = FixityDocument(**kwargs)
        setattr(self, 'name', schema.get_collection())
        setattr(self, 'schema', schema.to_dict())
        setattr(self, 'identifiers', schema.get_identifiers())
        setattr(self, 'uuid_type', schema.get_uuid_type())
        setattr(self, 'uuid_fields', schema.get_uuid_fields())
        self.setup()

    def index(self, filename, **kwargs):

        # Attempt to fetch the fixity record, as we need to pass any known
        # values to the indexer for comparison to the results from sync()
        self.name = normalize(filename)
        self.abs_filename = abspath(filename)
        file_uuid = self.get_typed_uuid(self.name)

        db_record = self.coll.find_one({'uuid': file_uuid})
        if db_record is None:
            # FIXME Find how to automate production of this template from schema
            db_record = {'name': filename,
                         'uuid': file_uuid,
                         'version': 0,
                         'child_of': []}

        indexer = FixityIndexer(self.abs_filename, schema=self.schema, **db_record).sync()
        fixity_record = indexer.to_dict()

        # lift over private keys to new document
        for key, value in db_record.items():
            if key.startswith('_'):
                fixity_record[key] = value
        # Now, update (or init) those same private keys
        fixity_record = self.set__private_keys(fixity_record, indexer.updated())
        # pprint(fixity_record)

        # Use basestore.Basestore for write
        resp = self.add_update_document(fixity_record, file_uuid, token=None)
        return resp

class StoreInterface(FixityStore):
    pass
