from .store import MeasurementDocument as Doc
from pprint import pprint

def get_schemas():
    schemas = dict()
    d1 = Doc()
    d2 = Doc()
    fname = getattr(d1, '_filename')
    document_schema = d1.to_jsonschema(document=True)
    object_schema = d2.to_jsonschema(document=False)
    schemas[fname] = object_schema
    schemas[fname + '_document'] = document_schema
    return schemas
