import inspect
import json
import os
import sys

from ...jsonschemas.schemas import JSONSchemaCollection
from ...linkedstores.basestore import DocumentSchema
from ...dicthelpers import data_merge

class SampleCatalogDocument(DocumentSchema):
    """Implements the composed schema representing all LinkedStore schemas"""

    def __init__(self, inheritance=True, **kwargs):
        schemaj = dict()
        try:
            modfile = inspect.getfile(self.__class__)
            schemafile = os.path.join(os.path.dirname(modfile), 'schema.json')
            schemaj = json.load(open(schemafile, 'r'))
            if inheritance is True:
                parent_modfile = inspect.getfile(self.__class__.__bases__[0])
                parent_schemafile = os.path.join(os.path.dirname(parent_modfile), 'schema.json')
                pschemaj = json.load(open(parent_schemafile, 'r'))
                schemaj = data_merge(pschemaj, schemaj)
        except Exception:
            raise
        params = {**schemaj, **kwargs}
        super(SampleCatalogDocument, self).__init__(**params)
        self.update_id()

def get_schemas():
    """Return schema(s) for SampleCatalogDocument

    Returns:
        JSONSchemaCollection: One or more schemas
    """
    schemas = JSONSchemaCollection(dict())
    d1 = SampleCatalogDocument()
    fname = getattr(d1, '_filename')
    object_schema = d1.to_jsonschema(document=True)
    schemas[fname] = object_schema
    return schemas