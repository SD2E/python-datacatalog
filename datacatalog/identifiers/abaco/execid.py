from .hashid import generate, validate, mock, \
    IdentifierSchema, JSONSchemaCollection

PROPERTIES = {'id': 'abaco_execid',
              'title': 'Abaco executionId',
              'description': 'Identifier for a specific Abaco execution',
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
