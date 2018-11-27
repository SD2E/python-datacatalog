import os
import sys
import importlib
import inspect
import itertools
from pprint import pprint
from ..debug_mode import debug_mode

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

# Primitives define schema enumerators or formats and are of a single JSON type
PRIMITIVE_SCHEMAS = ['definitions', 'filetypes', 'identifiers']
# Store schemas describe the object and document schemas for each managed
# document collection. Schemas inherit from basestore and are defined in each
# submodules document.json and filters.json. Linkages and constraints are
# defined in __extension properties in document.json. Store schemas are expected
# to reference the various primitive schemas in their composition.
STORE_SCHEMAS = ['linkedstores.basestore', 'linkedstores.challenge_problem', 'linkedstores.experiment_design', 'linkedstores.experiment', 'linkedstores.sample', 'linkedstores.measurement', 'linkedstores.file', 'linkedstores.fixity', 'linkedstores.pipeline', 'linkedstores.pipelinejob']
# Unmanaged schemas are built or imported from outside the datacatalog model.
# They are imported into the datacatalog model via a common base URI and
# filename namespace.
UNMANAGED_SCHEMAS = ['formats']
# Composed schemas are reference-based compositions of indvidual document,
# object, primitive, and unmanaged schemas
COMPOSED_SCHEMAS = ['compositions.sample_set']

SCHEMAS = [UNMANAGED_SCHEMAS, PRIMITIVE_SCHEMAS, STORE_SCHEMAS, COMPOSED_SCHEMAS]

class JSONSchemaCollection(dict):
    """Collection of schemas indexed by key"""
    def __new__(cls, value):
        return dict.__new__(cls, value)

def dynamic_import(module, package=None):
    return importlib.import_module(module, package='datacatalog')

def get_all_schemas(filters=[]):
    """Return all known JSON schemas

    Args:
        filters (list, optional): list of classes to inspect

    Returns:
        JSONSchemaCollection - Collection of schemas, keyed by name
    """
    schemata = JSONSchemaCollection(dict())
    for pkg in list(itertools.chain.from_iterable(SCHEMAS)):
        if debug_mode():
            print('SCHEMA PACKAGE', pkg)
        if isinstance(filters, list) and filters != []:
            if pkg not in filters:
                continue
        # print('SCHEMA: {}'.format(pkg))
        m = dynamic_import('.' + pkg + '.schemas')
        package_schemas = m.get_schemas()
        schemata = {**schemata, **package_schemas}
    return schemata
