import os
import sys
# from jsonschemas import JSONSchemaBaseObject

from .basestore import DocumentSchema

def get_schemas():
    d = DocumentSchema()
    fname = getattr(d, '_filename')
    return {fname: d.to_jsonschema()}
