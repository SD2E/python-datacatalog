import os
import sys
import importlib
import inspect
import itertools

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

UNMANAGED_SCHEMAS = []
PRIMITIVE_SCHEMAS = ['definitions', 'filetypes', 'identifiers']
STORE_SCHEMAS = ['linkedstores.basestore', 'linkedstores.challenge_problems', 'linkedstores.experiments', 'linkedstores.samples', 'linkedstores.measurements', 'linkedstores.files', 'linkedstores.fixities', 'linkedstores.pipelines', 'linkedstores.jobs']
COMPOSED_SCHEMAS = ['compositions.sample_set']

SCHEMAS = [UNMANAGED_SCHEMAS, PRIMITIVE_SCHEMAS, STORE_SCHEMAS, COMPOSED_SCHEMAS]
# SCHEMAS = [['linkedstores.basestore', 'linkedstores.challenge_problems']]
# SCHEMAS = [PRIMITIVE_SCHEMAS]

def dynamic_import(module, package=None):
    print(module, package)
    return importlib.import_module(module, package=package)

def get_all_schemas():
    schemata = dict()
    for pkg in list(itertools.chain.from_iterable(SCHEMAS)):
        m = dynamic_import(pkg + '.schemas')
        package_schemas = m.get_schemas()
        schemata = {**schemata, **package_schemas}
    return schemata
