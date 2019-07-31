from datacatalog.jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from datacatalog.utils import dynamic_import
from . import EVENT_NAMES
from .create import TagAnnotationCreateSchema
from .delete import TagAnnotationDeleteSchema
from .link import TagAnnotationLinkSchema
from .unlink import TagAnnotationUnlinkSchema

__all__ = ['TagAnnotationCreateSchema',
           'TagAnnotationDeleteSchema',
           'TagAnnotationLinkSchema',
           'TagAnnotationUnlinkSchema']

MODULES = EVENT_NAMES

def get_schemas():
    """Discovery and return known JSON schemas

    Returns:
        JSONSchemaCollection - Collection of schemas, keyed by name
    """
    schemata = dict()
    for pkg in MODULES:
        m = dynamic_import('.' + pkg, package='datacatalog.managers.annotations.tag')
        doc_schema = m.Schema()
        doc_fname = doc_schema._filename
        if doc_fname not in schemata:
            schemata[doc_fname] = doc_schema.to_jsonschema()
    return JSONSchemaCollection(schemata)
