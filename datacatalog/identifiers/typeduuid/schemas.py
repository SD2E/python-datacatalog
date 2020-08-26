"""Generates JSONschemas for the parent submodule
"""
from ...jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from ...utils import dynamic_import
from ..schemas import IdentifierSchema
from .typeduuid import uuidtypes, TypedCatalogUUID
from .examples import TYPEDUUID as EXAMPLES

def get_schemas():
    """Returns JSON schemas for each typed UUID
    """
    schemas = dict()
    for key, uuidt in uuidtypes.items():
        setup_args = {'_filename': key.title(),
                      'title': uuidt.title,
                      'prefix': uuidt.prefix,
                      'kind': key}
        schemas[key + '_uuid'] = TypedCatalogUUID(**setup_args).to_jsonschema()
    return JSONSchemaCollection(schemas)
