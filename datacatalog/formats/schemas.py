from .classify import get_converters
from jsonschemas import JSONSchemaBaseObject

def get_schemas():
    return get_classifier_schemas()

def get_classifier_schemas():
    schemas = dict()
    convs = get_converters()
    for conv in convs:
        schema_id = conv.filename + '_classifier'
        schema = conv.get_schema()
        schema['_filename'] = schema_id
        schemas[schema_id] = JSONSchemaBaseObject(**schema).to_jsonschema()
    return schemas
