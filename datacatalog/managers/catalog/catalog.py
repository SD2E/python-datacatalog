import json
import importlib
import inspect
import itertools
import os
import sys
import copy
from pprint import pprint

from ... import linkedstores
from ... import jsonschemas
from ...identifiers import typed_uuid

def dynamic_import(module, package='datacatalog'):
    return importlib.import_module(module, package=package)

class CatalogManagerError(linkedstores.basestore.CatalogError):
    pass

class CatalogManager(object):
    """Manager class for operations that span LinkedStore collections"""

    def __init__(self, mongodb_settings):
        # Assemble dict of stores keyed by classname
        self.stores = CatalogManager.init_stores(mongodb_settings)
        self.document = dict()

    @classmethod
    def init_stores(cls, mongodb_settings):
        # Assemble dict of stores keyed):
        stores = dict()
        for pkg in tuple(jsonschemas.schemas.STORE_SCHEMAS):
            try:
                m = dynamic_import('.' + pkg, package='datacatalog')
                store = m.StoreInterface(mongodb_settings)
                store_name = getattr(store, 'schema_name')
                store_basename = store_name.split('.')[-1]
                if store_basename != 'basestore':
                    stores[store_basename] = store
            except ModuleNotFoundError as mexc:
                print('Module not found: {}'.format(pkg), mexc)
        return stores

    def get_uuidtype(self, uuid):
        """Identify the type for a given UUID

        Args:
            uuid (str): UUID to classify by type

        Returns:
            str: Named type of the UUID
        """
        typed_uuid.validate(uuid)
        return typed_uuid.get_uuidtype(uuid)

    def get_by_uuid(self, uuid):
        """Returns a LinkedStore document by UUID

        Args:
            uuid (str): UUID of the document to retrieve

        Returns:
            dict: The document that was retrieved
        """
        storename = self.get_uuidtype(uuid)
        return self.stores[storename].find_one_by_uuid(uuid)

    def delete_by_uuid(self, uuid, token=None):
        """Deletes LinkedStore document and all linked references

        Args:
            uuid (str): UUID of the document to fully delete
            token (str, optional): Update token

        Returns:
            bool: Whether delete was successful or not
        """
        storename = self.get_uuidtype(uuid)
        self.stores[storename].coll.find_one_and_delete({'uuid': uuid})
        for name, store in self.stores.items():
            for linkage in linkedstores.basestore.store.BaseStore.LINK_FIELDS:
                store.coll.update_many({linkage: {'$in': [uuid]}}, {'$pull': {linkage: uuid}})
        return True

    def link(self, uuid1, uuid2, type='child_of', token=None):
        return False

    def unlink(self, uuid1, uuid2, type='child_of', token=None):
        return False
