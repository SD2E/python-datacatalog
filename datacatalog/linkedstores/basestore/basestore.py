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

from pprint import pprint
from slugify import slugify

from configs import CatalogStore
from jsonschemas import JSONSchemaBaseObject
from identifiers import typed_uuid
from utils import time_stamp

from .mongo import db_connection, ReturnDocument, UUID_SUBTYPE, ASCENDING, DuplicateKeyError
from .exceptions import *
from .exceptions import CatalogError
from .documentschema import DocumentSchema

class BaseStore(object):
    """Storage interface for JSON schema-informed documents"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):

        if isinstance(config.get('debug', None), bool):
            self.debug = config.get('debug')
        else:
            self.debug = False

        # This is a correlation string, akin to Reactor.nickname
        self.session = session

        # setup based on schema extended properties
        schema = DocumentSchema(**kwargs)
        self.schema = schema.to_dict()
        self.identifiers = schema.get_identifiers()
        self.name = schema.get_collection()
        self.uuid_type = schema.get_uuid_type()

        # database connection
        self.db = db_connection(mongodb)
        self.coll = self.db[self.name]

        # FIXME Integration with Agave configurations can be improved
        self.agave_system = CatalogStore.agave_storage_system
        self.base = CatalogStore.agave_root_dir
        self.store = CatalogStore.uploads_dir + '/'

        # self.difflog = LogStore(mongodb, config, session)

    def _post_init(self):
        if self.coll is not None:
            try:
                self.coll.create_index([('uuid', ASCENDING)], unique=True)
                self.coll.create_index([('child_of', ASCENDING)])
            except Exception as exc:
                raise CatalogError(
                    'Failed to set index on {}.uuid'.format(self.name), exc)

    def query(self, query={}):
        try:
            if not isinstance(query, dict):
                query = json.loads(query)
        except Exception as exc:
            raise CatalogError('Query was not resolvable as dict', exc)
        try:
            return self.coll.find(query)
        except Exception as exc:
            raise CatalogError('Qquery failed', exc)

    def query_by_identifier(self, **kwargs):
        try:
            resp = None
            for identifier in self.get_identifiers():
                query = dict()
                try:
                    query[identifier] = kwargs.get(identifier)
                except KeyError:
                    pass
                if query != {}:
                    resp = self.coll.find(query)
                    if resp is not None:
                        break
            return resp
        except Exception as exc:
            raise CatalogError('Query failed', exc)

    def delete_by_identifier(self, **kwargs):
        try:
            for identifier in self.get_identifiers():
                query = dict()
                try:
                    query[identifier] = kwargs.get(identifier)
                except KeyError:
                    pass
                if query != {}:
                    self.coll.remove(query)
        except Exception as exc:
            raise CatalogError('Delete failed', exc)
