import inspect
import json
import os
import sys

from ...jsonschemas.schemas import JSONSchemaCollection
from ...linkedstores.basestore import DocumentSchema
from ...dicthelpers import data_merge

class SampleSetDocument(DocumentSchema):
    """Implements the composed schema for a specific set of samples, measurements, and files"""

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
        super(SampleSetDocument, self).__init__(**params)
        self.update_id()

def get_schemas():
    """Return schema(s) for SampleSetDocument

    Returns:
        JSONSchemaCollection: One or more schemas
    """
    schemas = JSONSchemaCollection(dict())
    d1 = SampleSetDocument()
    fname = getattr(d1, '_filename')
    object_schema = d1.to_jsonschema(document=False)
    schemas[fname] = object_schema
    return schemas
