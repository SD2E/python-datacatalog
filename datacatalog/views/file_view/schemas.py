# NOTE: You must import submodule's named Class as Doc for schema and
# aggregation auto-discovery to work
from .classes import FixtyFileViewDocument as Doc
from ...jsonschemas.schemas import JSONSchemaCollection
from . import MONGODB_VIEW_NAME

__all__ = ['get_schemas', 'get_aggregation', 'MONGODB_VIEW_NAME']

def get_schemas():
    """Get schema(s) for ScienceView

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
    """Get the JSON document used to build this view in MongoDB

    Returns:
        MongoAggregation: A JSON document
    """
    d1 = Doc()
    return d1.get_aggregation()
