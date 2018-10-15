import os
import sys
import importlib
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

SCHEMAS = ['basestore', 'challenge_problems', 'experiments']
PRIMITIVES = ['identifiers', 'filetypes']

def dynamic_import(module, package=None):
    print(module, package)
    return importlib.import_module(module, package=package)

def get_all_schemas():
    schemas = get_schemas()
    primitives = get_primitives()
    schemas = {**schemas, **primitives}
    return schemas

def get_schemas():
    schemata = dict()
    for pkg in SCHEMAS:
        m = dynamic_import(pkg + '.schemas')
        package_schemas = m.get_schemas()
        schemata = {**schemata, **package_schemas}
    return schemata

def get_primitives():
    primitives = dict()
    return primitives

    for pkg in PRIMITIVES:
        m = dynamic_import(pkg + '.schemas')
        package_primitives = m.get_schemas()
        primitives = {**primitives, **package_primitives}
    return primitives
