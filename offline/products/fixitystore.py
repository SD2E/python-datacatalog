from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import os
import re

from ..identifiers.datacatalog_uuid import catalog_uuid, text_uuid_to_binary
from ..filesfixity import CatalogStore, ReturnDocument, FileFixityStore
from ..filesfixity import FileFixtyUpdateFailure, DuplicateFilenameError, DuplicateKeyError, FileFixtyNotFoundError
from ..utils import time_stamp
from ..dicthelpers import data_merge

from ..stores import STORES, level_to_config_attr, level_to_posix_path, store_to_posix_path
from .fixity import FileFixityInstance
STORE_NAME = 'products'
LEVEL = '1'

class ProductsFixityStore(FileFixityStore):
    """Create and manage fixity records for pipeline products
    Records are linked with ProductsMetadataStore records via common hash-based
    uuid for a given filename"""

    DEFAULTS = {'generated_by': [],
                'derived_from': [],
                'child_of': [],
                'properties': {},
                '_deleted': False,
                'level': LEVEL}

    def __init__(self, mongodb, config={}):
        super(ProductsFixityStore, self).__init__(mongodb, config={})
        coll = STORES[STORE_NAME]['fixity_collection']
        if self.debug:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()
        self.store = STORES[STORE_NAME]['prefix']
        self.base = store_to_posix_path(STORE_NAME)

    def index(self, filename, **kwargs):
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

    def create(self, filename, **kwargs):
        # Make sure only files that are supposed to be managed by this store are
        # being handled by it
        self.validate_filename(filename)
        filename = self.normalize(filename)
        filepath = self.abspath(filename)

        extras = data_merge(self.DEFAULTS, kwargs)
        # TODO normalize filename
        fixrec = FileFixityInstance(filename=filename,
            filepath=filepath, **extras).sync().as_dict(filters=['_filename'])
        try:
            res = self.coll.insert_one(fixrec)
            res_rec = self.coll.find_one({'_id': res.inserted_id})
            return res_rec
        except DuplicateKeyError:
            raise DuplicateFilenameError(
                'A file with this distinct path is already indexed. Try using update().')
        except Exception as exc:
            raise FileFixtyUpdateFailure(
                'Failed to index {}'.format(os.path.basename(filename)), exc)

    def update(self, filename, **kwargs):
        self.validate_filename(filename)
        filename = self.normalize(filename)
        filepath = self.abspath(filename)

        # fetch current record
        db_rec = self.coll.find_one({'name': filename})
        if db_rec is None:
            raise FileFixtyNotFoundError(
                'File {} has not yet been indexed. Try using create() first.'.format(os.path.basename(filename)))
        db_params = {}
        for k, v in self.DEFAULTS.items():
            try:
                db_params[k] = db_rec.get(k)
            except KeyError:
                pass
        db_params = data_merge(db_params, kwargs)
        fix_rec = FileFixityInstance(
            filename=filename, filepath=filepath, **db_params).sync().as_dict(filters=['_filename'])
        try:
            updated_rec = self.coll.find_one_and_replace(
                {'_id': db_rec['_id']}, fix_rec,
                return_document=ReturnDocument.AFTER)
            return updated_rec
        except Exception as exc:
            raise FileFixtyUpdateFailure(
                'Failed to update index for {}'.format(os.path.basename(filename)), exc)

    def delete(self, filename, force=False):
        """Delete the record by setting to indeleted. Actually delete if forced to."""
        if not force:
            return self.update(filename, _deleted=False)
        else:
            try:
                return self.coll.delete_one({'name': filename})
            except Exception:
                raise FileFixtyUpdateFailure(
                    'Unable to delete {}'.format(os.path.basename(filename)))

    def undelete(self, filename, force=False):
        """Undelete the record if possible"""
        try:
            return self.update(filename, _deleted=True)
        except FileFixtyUpdateFailure:
            raise FileFixtyUpdateFailure(
                'Index for file {} was not found: Perhaps it was force-deleted.'.format(os.path.basename(filename)))

    def validate_filename(self, filename):
        filename = re.compile('^\/+').sub('', filename)
        if not filename.startswith(self.store):
            raise FileFixtyUpdateFailure(
                'Only files in store "{}" can be indexed'.format(STORE_NAME))
        else:
            return True

    def normalize(self, filename):
        # Strip leading /
        filename = re.compile('^\/+').sub('', filename)
        if filename.startswith(self.store):
            filename = filename[len(self.store):]
        return filename

    def abspath(self, filename):
        if filename.startswith('/'):
            filename = filename[1:]
        if filename.startswith(self.store):
            filename = filename[len(self.store):]
        return os.path.join(self.base, self.store, filename)
