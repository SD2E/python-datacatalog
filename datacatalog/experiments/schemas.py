import os
import sys
# from jsonschemas import JSONSchemaBaseObject

from .store import ExperimentDocument

def get_schemas():
    d = ExperimentDocument()
    fname = getattr(d, '_filename')
    return {fname: d.to_jsonschema()}
