import json
import importlib
import inspect
import itertools
import os
import sys
from pprint import pprint

from ..linkedstores import DEFAULT_LINK_FIELDS
from .. import linkedstores
from .. import jsonschemas
from ..utils import dynamic_import
from ..tenancy import current_tenant_uri
from ..dicthelpers import data_merge
from ..agavehelpers import from_agave_uri
from ..identifiers import typeduuid
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
        return self.linkage_from_inputs(inputs=inputs, target='derived_from')

    def generator_from_inputs(self, inputs=[]):
        return self.linkage_from_inputs(inputs=inputs, target='generated_by')

    def parent_from_inputs(self, inputs=[]):
        return self.linkage_from_inputs(inputs=inputs, target='child_of')

    def self_from_inputs(self, inputs=[]):
        return self.linkage_from_inputs(inputs=inputs, target='self')

    def linkage_from_inputs(self, inputs=[], target='child_of'):
        """Retrieve linkage targets from a set of inputs

        Filepaths will be resolved against the ``file``
        collection and will return a reference to their immediate
        parent. URIs will be resolved against the ``reference`` collection
        and will return a reference to themselves.

        Args:
            inputs (list): Identifier values for one or more inputs (e.g. ``name``, ``file_id``, ``uri``)
            target (str): Linkage type to retrieve

        Returns:
            list: a set of Typed UUIDs
        """
        # STORES = [('file', 'name', 'child_of')]
        STORES = [('reference', ['uri', 'reference_id'], target),
                  ('file', ['name', 'file_id'], target)]

        if target not in DEFAULT_LINK_FIELDS and target != 'self':
            raise ValueError(
                "{} is an invalid value for 'target'. Valid options include: {}".format(target, DEFAULT_LINK_FIELDS))

        links = list()
        for store_name, search_keys, linkage in STORES:
            for idstr in inputs:
                if not isinstance(idstr, str):
                    raise ValueError(
                        "{} is a {} not a string".format(idstr, type(idstr)))
                for key in search_keys:
                    # Resolve agave URL into file.name
                    if store_name == 'file' and key == 'name' and idstr.startswith('agave:'):
                        agsys, agpath, agfile = from_agave_uri(idstr)
                        idstr = os.path.join(agpath, agfile)
                    query = {key: idstr}
                    resp = self.stores[store_name].find_one_by_id(**query)
                    if resp is not None:
                        if linkage == 'self':
                            links.extend([resp.get('uuid')])
                        else:
                            links.extend(resp.get(linkage, []))
                        continue

        # Filter out anything that may have come back that's not a UUID
        # Set permissive to True to simply filter out values that dont validate
        uuid_links = [l for l in links if typeduuid.validate(
            l, permissive=False) is True]
        uuid_links = sorted(list(set(uuid_links)))
        return uuid_links
