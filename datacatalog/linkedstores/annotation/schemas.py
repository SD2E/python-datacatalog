from ...jsonschemas import JSONSchemaCollection
from .inline import InlineAnnotationSchema as Inline
from .annotation import AnnotationSchema as Anno

# from .store import DocumentSchema as Doc
# from .store import JSONSchemaCollection

def get_schemas():
    """Get JSON schemas for this submodule

    Returns:
        dict: Return the object and document JSON schema that define the store
    """
    schemas = JSONSchemaCollection(dict())
    d1 = Anno()
    d2 = Inline()

    fname1 = d1.get_filename()
    anno_object_schema = d1.to_jsonschema(document=False)
    schemas[fname1] = anno_object_schema

    fname2 = d1.get_filename(document=True)
    anno_document_schema = d1.to_jsonschema(document=True)
    schemas[fname2] = anno_document_schema

    fname3 = d2.get_filename()
    inline_object_schema = d2.to_jsonschema(document=False)
    schemas[fname3] = inline_object_schema

    return schemas
