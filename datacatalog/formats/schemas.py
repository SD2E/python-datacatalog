from ..linkedstores.basestore.store import JSONSchemaCollection
from ..jsonschemas import JSONSchemaBaseObject
from .classify import get_converters

def get_schemas():
    """Get JSON schemas for Classifiers

    Returns:
        JSONSchemaCollection: Object and document JSON schema that define the store
    """
    return JSONSchemaCollection(__get_classifier_schemas())

def __get_classifier_schemas():
    schemas = dict()
    convs = get_converters()
    for conv in convs:
        schema_id = conv.filename + '_classifier'
        schema = conv.get_schema()
        schema['_filename'] = schema_id
        schemas[schema_id] = JSONSchemaBaseObject(**schema).to_jsonschema()
    return schemas
