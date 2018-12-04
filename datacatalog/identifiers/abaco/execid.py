from .hashid import *

PROPERTIES = {'id': 'abaco_execid',
              'title': 'Abaco executionID',
              'description': 'Abaco executionID identifier',
              'type': 'string'}

__all__ = ["generate", "validate", "mock", "get_schemas"]

def get_schemas():
    schemas = dict()
    doc = {'_filename': PROPERTIES['id'],
           'description': PROPERTIES['description'],
           'type': PROPERTIES['type']}
    sch = IdentifierSchema(**doc).to_jsonschema()
    schemas[PROPERTIES['id']] = sch
    return JSONSchemaCollection(schemas)
