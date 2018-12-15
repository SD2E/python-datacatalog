# NOTE: You must import submodule's named Class as Doc for schema and
# aggregation auto-discovery to work
from .classes import MongoViewDocument as Doc
from ...jsonschemas.schemas import JSONSchemaCollection
from . import mongodb_view_name

__all__ = ['get_schemas', 'get_aggregation', 'mongodb_view_name']

def get_schemas():
    """Get schema(s) for a MongoViewDocument

    Returns:
        JSONSchemaCollection: One or more schemas indexed by filename
    """
    schemas = JSONSchemaCollection(dict())
    d1 = Doc()
    fname = getattr(d1, '_filename')
    object_schema = d1.to_jsonschema(document=False)
    schemas[fname] = object_schema
    return schemas

def get_aggregation():
    """Get the JSON document used in constructing this view

    Returns:
        MongoAggregation: A JSON document
    """
    d1 = Doc()
    return d1.get_aggregation()
