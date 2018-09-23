from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import os
from ..identifiers.datacatalog_uuid import catalog_uuid
from ..filesfixity import CatalogStore, ReturnDocument, FileFixityStore
from ..filesfixity import FileFixtyUpdateFailure, DuplicateFilenameError, DuplicateKeyError
from ..utils import time_stamp
from ..dicthelpers import data_merge

from .fixity import FileFixityInstance

class ProductsFixityStore(FileFixityStore):
    """Create and manage fixity records for pipeline products
    Records are linked with ProductsMetadataStore records via common hash-based
    uuid for a given filename"""

    DEFAULTS = {'generated_by': [],
                'derived_from': [],
                'child_of': [],
                'properties': {},
                '_deleted': True}

    def __init__(self, mongodb, config={}):
        super(ProductsFixityStore, self).__init__(mongodb, config={})
        coll = self.collections.get('products_files_fixity')
        if self.debug:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()
        self.store = CatalogStore.products_dir + '/'

    def create(self, filename, **kwargs):
        self.filename = self.normalize(filename)
        self.filepath = self.abspath(self.filename)
        extras = data_merge(self.DEFAULTS, kwargs)
        # TODO normalize filename
        fixrec = FileFixityInstance(filename=self.filename,
            filepath=self.abspath(self.filename), **extras).sync().as_dict(filters=['_filename'])
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
        self.filename = self.normalize(filename)
        # fetch current record
        db_rec = self.coll.find_one({'filename': filename})
        if db_rec is None:
            raise FileFixtyUpdateFailure('File {} has not yet been indexed. Try using create() first.'.format(os.path.basename(filename)))
        db_params = {}
        for k, v in self.DEFAULTS.items():
            try:
                db_params[k] = db_rec.get(k)
            except KeyError:
                pass
        db_params = data_merge(db_params, kwargs)
        fix_rec = FileFixityInstance(
            self.filename, filepath=self.abspath(self.filename), **db_params).sync().as_dict(filters=['_filename'])
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
                return self.coll.remove({'filename': filename})
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
