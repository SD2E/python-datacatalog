from ...jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from ...utils import dynamic_import
from ..schemas import IdentifierSchema
from .typeduuid import UUIDType, TypedCatalogUUID

MODULES = ('appid', 'uuids')

def get_schemas():
    schemas = dict()
    for key, uuidt in UUIDType.items():
        setup_args = {'_filename': key.title(),
                      'title': uuidt.title + ' UUID',
                      'prefix': uuidt.prefix}
        schemas[key + '_uuid'] = TypedCatalogUUID(**setup_args).to_jsonschema()
    return JSONSchemaCollection(schemas)