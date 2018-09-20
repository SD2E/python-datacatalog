
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *
from builtins import object

import json
import copy
import datetime
from slugify import slugify

from .mongo import db_connection, ReturnDocument, UUID_SUBTYPE
from .configs import CatalogStore
from .utils import catalog_uuid, current_time, time_stamp, validate_file_to_schema
from .dicthelpers import data_merge, dict_compare, filter_dict, json_diff, data_merge_diff
from .constants import Constants, Mappings, Enumerations
from .exceptions import CatalogError

class LogStoreError(CatalogError):
    pass

class LogStore(object):
    def __init__(self, mongodb, config={}, session=None):
        self.db = db_connection(mongodb)
        if isinstance(config.get('debug', None), bool):
            self.debug = config.get('debug')
        else:
            self.debug = False

        coll = CatalogStore.collections['updates']
        if self.debug:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])

        self.name = coll
        self.coll = self.db[coll]
        self.session = session

    def append(self, collection_name, uuid, diff):
        """Write a JSON diff to the update log, extended with source
        collection and uuid.
        """
        ts = current_time()
        # Do not log the empties as they should not count as updates
        if diff != {}:
            # filter dict to remove $
            sdiff = safen(diff)
            rec = {'created_date': ts, 'ref': {
                'collection': collection_name, 'uuid': uuid}, 'diff': sdiff}
            if self.session is not None:
                rec['ref']['session'] = self.session
            try:
                result = self.coll.insert_one(rec)
                return self.coll.find_one({'_id': result.inserted_id})
            except Exception as exc:
                raise LogStoreError('failed to log update', exc)


def safen(d):
    """Replaces $ leading character in keys with _$, making the dict safe for MongoDB"""
    new = {}
    for k, v in list(d.items()):
        if isinstance(v, dict):
            v = safen(v)
        if isinstance(k, str):
            new[k.replace('$', '_$')] = v
    return new
