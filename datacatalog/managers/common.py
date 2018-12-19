import json
import importlib
import inspect
import itertools
import os
import sys
from pprint import pprint

from .. import linkedstores
from .. import jsonschemas
from ..utils import dynamic_import
from ..tenancy import current_tenant_uri
from ..dicthelpers import data_merge

# def dynamic_import(module, package='datacatalog'):
#     return importlib.import_module(module, package=package)

class ManagerError(linkedstores.basestore.CatalogError):
    """Error has occurred inside a Manager"""
    pass

class Manager(object):
    """Manages operations across LinkedStores"""

    def __init__(self, mongodb, agave=None, *args, **kwargs):
        # Assemble dict of stores keyed by classname
        self.stores = Manager.init_stores(mongodb, agave=agave)
        self.api_server = kwargs.get('api_server', current_tenant_uri())

    @classmethod
    def init_stores(cls, mongodb, agave=None):
        # Assemble dict of stores keyed):
        stores = dict()
        for pkg in tuple(jsonschemas.schemas.STORE_SCHEMAS):
            try:
                m = dynamic_import('.' + pkg, package='datacatalog')
                store = m.StoreInterface(mongodb, agave=agave)
                store_name = getattr(store, 'schema_name')
                store_basename = store_name.split('.')[-1]
                stores[store_basename] = store
            except ModuleNotFoundError as mexc:
                print('Module not found: {}'.format(pkg), mexc)
        return stores

    def derivation_from_inputs(self, inputs=[]):
        """Build ``derived_from`` from a set of inputs

        Filepaths will be resolved against the ``file``
        collection and will return a reference to their immediate
        parent. URIs will be resolved against the ``reference`` collection
        and will return a reference to themselves.

        Args:
            inputs (str): One or more filepaths or URIs

        Returns:
            list: a set of Typed UUIDs
        """
        STORES = [('file', 'name', 'child_of')]
#        STORES = [('file', 'name', 'child_of'), ('reference', 'uri', 'self')]

        derivs = list()
        for idstr in inputs:
            for storename, key, linkage in STORES:
                query = {key: idstr}
                resp = self.stores[storename].find_one_by_id(**query)
                if resp is not None:
                    if linkage == 'self':
                        derivs.extend(resp.get('uuid'))
                    else:
                        derivs.extend(resp.get(linkage, []))
                    continue
        derivs = sorted(list(set(derivs)))
        return derivs
