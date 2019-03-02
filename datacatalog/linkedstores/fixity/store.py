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
from ...identifiers.typeduuid import catalog_uuid
from ...pathmappings import normalize, abspath, relativize, normpath
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, JSONSchemaCollection
from .schema import FixityDocument
from .indexer import FixityIndexer
from .exceptions import FixtyUpdateFailure, FixityDuplicateError, FixtyNotFoundError

# FixityStore is a special case of LinkedStore that creates and manages its
# own records. This is accomplished declaratively using the ``index()`` method.

class FixityStore(LinkedStore):
    """Defines fixed attributes for a managed file"""

    LINK_FIELDS = ['child_of', 'generated_by']

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
            filename (str): Agave-canonical absolute path to the target file

        Returns:
            dict: A LinkedStore document containing fixity details
        """
        # print('FIXITY.STORE.INDEX ' + filename)
        self.name = normpath(filename)
        self.abs_filename = abspath(self.name)
        fixity_uuid = self.get_typeduuid(self.name)
        # Look up the FileStore UUID as it will be used to establish the Fixity
        # record as its child
        file_uuid = catalog_uuid(self.name, uuid_type='file')

        db_record = self.coll.find_one({'uuid': fixity_uuid})

        if db_record is None:
            # TODO - generated_by should default to a global settting
            db_record = {'name': filename,
                         'uuid': fixity_uuid,
                         'version': 0,
                         'child_of': [file_uuid],
                         'generated_by': kwargs.get('generated_by', [])}
        else:
            # This is special case logic. Fixity is a managed record, so it
            # is not permitted to have arbitrary values for generated_by. We
            # instead maintain the most recent instance of generated_by
            try:
                gen_by = kwargs.get('generated_by', db_record.get('generated_by', []))
                if isinstance(gen_by, str):
                    gen_by = [gen_by]
                db_record['generated_by'] = gen_by
            except Exception:
                raise
        # pprint(db_record)
        indexer = FixityIndexer(schema=self.schema, **db_record).sync()
        fixity_record = indexer.to_dict()
        # print('FIXITYRECORD')
        # pprint(fixity_record)

        # lift over private keys to new document
        for key, value in db_record.items():
            if key.startswith('_'):
                fixity_record[key] = value
        # Now, update (or init) those same private keys
        fixity_record = self.set_private_keys(fixity_record, indexer.updated())

        resp = self.add_update_document(fixity_record, fixity_uuid, token=None)
        return resp

    def get_typeduuid(self, payload, binary=False):
        identifier_string = None
        if isinstance(payload, dict):
            if 'name' in payload:
                payload['name'] = normpath(payload['name'])
            identifier_string = self.get_linearized_values(payload)
        else:
            identifier_string = normpath(str(payload))
        return super().get_typeduuid(identifier_string, binary)

class StoreInterface(FixityStore):
    pass
