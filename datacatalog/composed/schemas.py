from .store import MetadataDocument

def get_schemas():
    d = MetadataDocument()
    fname = getattr(d, '_filename')
    return {fname: d.to_jsonschema()}
