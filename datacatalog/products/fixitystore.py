from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import os
from ..filesfixity import ReturnDocument, FileFixityStore, FileFixtyUpdateFailure, DuplicateFilenameError, DuplicateKeyError
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
                '_visible': True}

    def __init__(self, mongodb, config={}):
        super(ProductsFixityStore, self).__init__(mongodb, config={})
        coll = self.collections.get('products_files_fixity')
        if self.debug:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()

    def create(self, filename, **kwargs):
        extras = data_merge(self.DEFAULTS, kwargs)
        # TODO normalize filename
        fixrec = FileFixityInstance(filename, **extras).sync().as_dict()
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
        # TODO normalize filename

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
        fix_rec = FileFixityInstance(filename, **db_params).sync()
        try:
            updated_rec = self.coll.find_one_and_replace(
                {'_id': db_rec['_id']}, fix_rec,
                return_document=ReturnDocument.AFTER)
            return updated_rec
        except Exception as exc:
            raise FileFixtyUpdateFailure(
                'Failed to update index for {}'.format(os.path.basename(filename)), exc)

