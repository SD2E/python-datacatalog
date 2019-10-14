import inspect
import json
import os
import sys
import time
from pprint import pprint
from datacatalog import settings
from ...dicthelpers import data_merge
from ...identifiers.typeduuid import catalog_uuid
from ...stores import abspath
from ...utils import normalize, normpath
from ..basestore import AgaveClient, LinkedStore, CatalogUpdateFailure, linkages
from ..basestore import HeritableDocumentSchema, JSONSchemaCollection
from ..basestore import RateLimiter, RateLimitExceeded
from .schema import FixityDocument
from .indexer import FixityIndexer
from .exceptions import FixtyUpdateFailure, FixityDuplicateError, FixtyNotFoundError

DEFAULT_LINK_FIELDS = [linkages.CHILD_OF]
# FixityStore is a special case of LinkedStore that creates and manages its
# own records. This is accomplished declaratively using the ``index()`` method.

class FixityStore(AgaveClient, LinkedStore, RateLimiter):
    """Defines fixed attributes for a managed file"""

    LINK_FIELDS = DEFAULT_LINK_FIELDS
    LOG_JSONDIFF_UPDATES = False

    def __init__(self, mongodb, agave=None, config={}, session=None, **kwargs):
        super(FixityStore, self).__init__(mongodb, config, session, agave=agave)
        # LinkedStore.__init__(self, mongodb, config, session, agave=agave)
        schema = FixityDocument(**kwargs)
        super(FixityStore, self).update_attrs(schema)
        # LinkedStore.update_attrs(self, schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))
        RateLimiter.__init__(self, **kwargs)

    def index(self, filename, storage_system=None, **kwargs):
        """Capture or update current properties of a file

        Fixity includes creation and modification date (rounded to msec), sha256
        checksum, size in bytes, and inferred file type.

        Args:
            filename (str): Agave-canonical absolute path to the target
            storage_system (str, optional): Agave storage system for the target

        Returns:
            dict: A LinkedStore document containing fixity details
        """
        # print('FIXITY.STORE.INDEX ' + filename)
        if storage_system is None:
            storage_system = settings.STORAGE_SYSTEM
        self.name = normpath(filename)
        self.abs_filename = self._helper.mapped_posix_path(
            self.name, storage_system=storage_system)
        fixity_uuid = self.get_typeduuid(self.name)
        # Look up the FileStore UUID as it will be used to establish the Fixity
        # record as its child
        file_uuid = catalog_uuid(self.name, uuid_type='file')

        db_record = self.coll.find_one({'uuid': fixity_uuid})

        if db_record is None:
            db_record = {'name': filename,
                         'storage_system': storage_system,
                         'uuid': fixity_uuid,
                         'version': 0,
                         'child_of': [file_uuid]}

        # Invoke the RateLimiter that we've mixed in via MultipleInheritance
        self.limit()
        indexer = FixityIndexer(schema=self.schema,
                                agave=self._helper.client,
                                **db_record).sync()
        fixity_record = indexer.to_dict()

        # lift over private keys to new document
        for key, value in db_record.items():
            if key.startswith('_'):
                fixity_record[key] = value
        # Now, update (or init) those same private keys
        fixity_record = self.set_private_keys(fixity_record, indexer.updated())

        resp = self.add_update_document(fixity_record, uuid=fixity_uuid,
                                        token=kwargs.get('token', None))
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
