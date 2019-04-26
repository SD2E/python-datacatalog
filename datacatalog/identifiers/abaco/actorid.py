from .hashid import generate, validate, mock, \
    IdentifierSchema, JSONSchemaCollection
from .examples import ABACO_ACTOR_ID as EXAMPLES

PROPERTIES = {'id': 'abaco_actorid',
              'title': 'Abaco actorId',
              'description': 'Identifer for an Abaco actor',
              'type': 'string'}

__all__ = ["generate", "validate", "mock", "get_schemas"]

def get_schemas():
    schemas = dict()
    doc = {'_filename': PROPERTIES['id'],
           'description': PROPERTIES['description'],
           'type': PROPERTIES['type'],
           'examples': EXAMPLES}
    sch = IdentifierSchema(**doc).to_jsonschema()
    schemas[PROPERTIES['id']] = sch
    return JSONSchemaCollection(schemas)
