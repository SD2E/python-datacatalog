from datacatalog.jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from datacatalog.utils import dynamic_import

MODULES = ('tag', 'text')

def get_schemas():
    """Discovery and return known JSON schemas

    Returns:
        JSONSchemaCollection - Collection of schemas, keyed by name
    """
    schemata = dict()
    for pkg in MODULES:
        m = dynamic_import('.' + pkg, package='datacatalog.managers.annotations')
        schemas = m.get_schemas()
        schemata = {**schemata, **schemas}
    return JSONSchemaCollection(schemata)
