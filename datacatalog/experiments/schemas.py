from .store import ExperimentDocument as Doc

def get_schemas():
    schemas = dict()
    d = Doc()
    fname = getattr(d, '_filename')
    document_schema = d.to_jsonschema()
    object_schema = d.to_jsonschema(document=True)
    schemas[fname] = object_schema
    schemas[fname + '_document'] = document_schema
    return schemas
