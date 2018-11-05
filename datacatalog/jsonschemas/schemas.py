import os
import sys
import importlib
import inspect
import itertools
from pprint import pprint

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

UNMANAGED_SCHEMAS = []
PRIMITIVE_SCHEMAS = ['definitions', 'filetypes', 'identifiers']
# STORE_SCHEMAS = ['linkedstores.file', 'linkedstores.fixity']
STORE_SCHEMAS = ['linkedstores.basestore', 'linkedstores.challenge_problem', 'linkedstores.experiment_design', 'linkedstores.experiment', 'linkedstores.sample', 'linkedstores.measurement', 'linkedstores.file', 'linkedstores.fixity', 'linkedstores.pipeline', 'linkedstores.pipelinejob']
COMPOSED_SCHEMAS = ['compositions.sample_set']

SCHEMAS = [UNMANAGED_SCHEMAS, PRIMITIVE_SCHEMAS, STORE_SCHEMAS, COMPOSED_SCHEMAS]

def dynamic_import(module, package=None):
    return importlib.import_module(module, package='..datacatalog')

def get_all_schemas():
    schemata = dict()
    for pkg in list(itertools.chain.from_iterable(SCHEMAS)):
        m = dynamic_import(pkg + '.schemas')
        package_schemas = m.get_schemas()
        schemata = {**schemata, **package_schemas}
    return schemata
