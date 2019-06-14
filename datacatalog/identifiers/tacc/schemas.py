from ...jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from ...utils import dynamic_import
from ..schemas import IdentifierSchema

MODULES = ['username']

def get_schemas():
    """Discovery and return known JSON schemas

    Returns:
        JSONSchemaCollection - Collection of schemas, keyed by name
    """
    schemata = JSONSchemaCollection(dict())
    for pkg in MODULES:
        m = dynamic_import('.' + pkg, package='datacatalog.identifiers.tacc')
        package_schemas = m.get_schemas()
        schemata = {**schemata, **package_schemas}
    return JSONSchemaCollection(schemata)
