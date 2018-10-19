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
from ..basestore import BaseStore, CatalogUpdateFailure, DocumentSchema, HeritableDocumentSchema, time_stamp
from .exceptions import FixtyUpdateFailure, FixityDuplicateError, FixtyNotFoundError

# FixityStore is special since it responsible for creating the record as well as
# storing it. This is implemented by giving it an index() method, which in turn
# instantiates a FixityIndexer that has sync() and render() methods to capture
# and render fixity details into a storable document.

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

        indexer = FixityIndexer(filename, **kwargs).sync()

        self.validate_filename(filename)

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
