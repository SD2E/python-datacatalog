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
from pprint import pprint

from .schema import FixityDocument
from .indexer import FixityIndexer
from ..basestore import BaseStore, CatalogUpdateFailure, DocumentSchema, HeritableDocumentSchema, time_stamp
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
        setattr(self, 'uuid_field', schema.get_uuid_field())
        self.setup()

    def index(self, filename, **kwargs):

        # Attempt to fetch the fixity record, as we need to pass any known
        # values to the indexer for comparison to the results from sync()
        self.filename = self.normalize(filename)
        self.abs_filename = self.abspath(filename)
        file_uuid = self.get_typed_uuid(self.filename, self.uuid_type)
        db_record = self.find_one_by_id(file_uuid)
        if db_record is None:
            db_record = {}

        indexer = FixityIndexer(filename, schema=self.schema, **db_record).sync()

        # This is not great practice to modify kwargs
        gb = []
        if kwargs.get('generated_by'):
            for guid in kwargs.get('generated_by'):
                if isinstance(guid, str):
                    try:
                        gb.append(text_uuid_to_binary(guid))
                    except Exception:
                        pass
            kwargs['generated_by'] = gb

        try:
            return self.update(filename, **kwargs)
        except FileFixtyNotFoundError:
            return self.create(filename, **kwargs)
        except Exception as exc:
            raise FileFixtyUpdateFailure(exc)
