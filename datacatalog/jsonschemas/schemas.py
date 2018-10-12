import importlib
# from .. import identifiers

def dynamic_import(module, package=None):
    print(module, package)
    return importlib.import_module(module, package=package)

def get_all_schemas():
    schemas = dict()
    primitives = get_primitives()
    schemas = {**schemas, **primitives}
    return schemas

def get_primitives():
    PACKAGES = ['identifiers', 'filetypes']
    primitives = dict()
    for pkg in PACKAGES:
        m = dynamic_import(pkg + '.schemas')
        package_primitives = m.get_schemas()
        primitives = {**primitives, **package_primitives}
    return primitives
