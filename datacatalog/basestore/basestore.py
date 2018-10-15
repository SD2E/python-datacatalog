from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object

import os
import sys
import inspect
import json
import copy
import datetime

from slugify import slugify

from configs import CatalogStore
from jsonschemas import JSONSchemaBaseObject
from identifiers import typed_uuid
from .mongo import db_connection, ReturnDocument, UUID_SUBTYPE, ASCENDING, DuplicateKeyError
from .exceptions import *

class DocumentSchema(JSONSchemaBaseObject):
    def __init__(self, **kwargs):
        modfile = inspect.getfile(self.__class__)
        try:
            schemafile = os.path.join(os.path.dirname(modfile), 'document.json')
            schemaj = json.load(open(schemafile, 'r'))
        except:
            schemaj = dict()
        params = {**schemaj, **kwargs}
        super(DocumentSchema, self).__init__(**params)
        self.update_id()

    def collection(self):
        """MongoDB collection for this document type"""
        return getattr(self, '__collection')

    def indexes(self):
        pass

class BaseStore(object):
    TYPED_UUID_TYPE = 'generic'
    def __init__(self, mongodb, config={}, session=None, **kwargs):

        if isinstance(config.get('debug', None), bool):
            self.debug = config.get('debug')
        else:
            self.debug = False

        self.schema = DocumentSchema(**kwargs).to_dict()
        self.db = db_connection(mongodb)
        self.collections = CatalogStore.collections

        self.agave_system = CatalogStore.agave_storage_system
        self.base = CatalogStore.agave_root_dir
        self.store = CatalogStore.uploads_dir + '/'
        self.coll = None
        self.name = None
        self.difflog = LogStore(mongodb, config, session)
        self.session = session

    def _post_init(self):
        if self.coll is not None:
            try:
                self.coll.create_index([('uuid', ASCENDING)], unique=True)
                self.coll.create_index([('child_of', ASCENDING)])
            except Exception as exc:
                raise CatalogDatabaseError(
                    'Failed to set index on {}.uuid'.format(self.name), exc)

    def query(self, query={}):
        try:
            if not isinstance(query, dict):
                query = json.loads(query)
        except Exception as exc:
            raise CatalogQueryError('query was not resolvable as dict', exc)
        try:
            return self.coll.find(query)
        except Exception as exc:
            raise CatalogQueryError('query failed')

    def query_by_uuid(self, query={}):
        try:
            if not isinstance(query, dict):
                query = json.loads(query)
        except Exception as exc:
            raise CatalogQueryError('query was not resolvable as dict', exc)
        try:
            return self.coll.find(query)
        except Exception as exc:
            raise CatalogQueryError('query failed')

    def delete_by_uuid(self, uuid):
        '''Delete record by uuid'''
        try:
            return self.coll.remove({'uuid': uuid})
        except Exception:
            raise CatalogUpdateFailure('Delete failed')
