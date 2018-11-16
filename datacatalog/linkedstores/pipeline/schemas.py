from .store import PipelineDocument as Doc
from pprint import pprint

def get_schemas():
    """Get JSON schemas for PipelineDocument

    Returns:
        dict: Return the object and document JSON schema that define the store
    """
    schemas = dict()

    d1 = Doc()
    d2 = Doc()

    fname1 = d1.get_filename(document=True)
    fname2 = d2.get_filename()

    document_schema = d1.to_jsonschema(document=True)
    object_schema = d2.to_jsonschema(document=False)

    schemas[fname1] = document_schema
    schemas[fname2] = object_schema

    return schemas
