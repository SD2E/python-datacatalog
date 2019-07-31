from datacatalog.jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from datacatalog.utils import dynamic_import
from . import EVENT_NAMES
from .create import TextAnnotationCreateSchema
from .delete import TextAnnotationDeleteSchema
from .reply import TextAnnotationReplySchema

__all__ = ['TextAnnotationCreateSchema', 'TextAnnotationReplySchema',
           'TextAnnotationDeleteSchema']

MODULES = EVENT_NAMES

def get_schemas():
    """Discovery and return known JSON schemas

    Returns:
        JSONSchemaCollection - Collection of schemas, keyed by name
    """
    schemata = dict()
    for pkg in MODULES:
        m = dynamic_import('.' + pkg, package='datacatalog.managers.annotations.text')
        doc_schema = m.Schema()
        doc_fname = doc_schema._filename
        if doc_fname not in schemata:
            schemata[doc_fname] = doc_schema.to_jsonschema()
    return JSONSchemaCollection(schemata)
