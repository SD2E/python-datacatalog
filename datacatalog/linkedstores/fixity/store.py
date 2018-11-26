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
from ...pathmappings import normalize, abspath, relativize
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema
from .schema import FixityDocument
from .indexer import FixityIndexer
from .exceptions import FixtyUpdateFailure, FixityDuplicateError, FixtyNotFoundError

# FixityStore is a special case, as creates and manages its records as well as
# storing them. This is implemented in its index() method, which in turn
# instantiates a FixityIndexer. That object has sync() and render(), which
# capture the latest fixity data and render it into a JSON doc.

class FixityStore(LinkedStore):
    """Defines physical properties for a file"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(FixityStore, self).__init__(mongodb, config, session)
        schema = FixityDocument(**kwargs)
        super(FixityStore, self).update_attrs(schema)
        self.setup()

    def index(self, filename, **kwargs):
        """Capture or update current properties of a file

        Fixity includes creation and modification date (rounded to msec), sha256
        checksum, size in bytes, and inferred file type.

        Args:
            filename (str): Absolute, Agave-relative path to the target file

        Returns:
            dict: The LinkedStore document containing fixity details
        """
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
        fixity_record = self.set_private_keys(fixity_record, indexer.updated())
        # pprint(fixity_record)

        # Use basestore.Basestore for write
        resp = self.add_update_document(fixity_record, file_uuid, token=None)
        return resp

class StoreInterface(FixityStore):
    pass
