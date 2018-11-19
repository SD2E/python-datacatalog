import json
import os
import sys
from ..jsonschemas import JSONSchemaBaseObject

HERE = os.path.abspath(__file__)
PARENT = os.path.dirname(HERE)

def get_schemas():
    """Return definition schema(s)

    Returns:
        dict: One or more schemas"""
    jsondocs = build_jsondocs()
    templated_jsondocs = build_templates()
    schemas = {**jsondocs, **templated_jsondocs}
    return schemas

def build_jsondocs():
    """Discover and return schema definitions in `jsondocs`"""
    schemas = dict()
    docs_dir = os.path.join(PARENT, 'jsondocs')
    for jdoc in os.listdir(docs_dir):
        if jdoc.endswith('.json'):
            filename = os.path.basename(jdoc).lower().replace('.json', '')
            filepath = os.path.join(docs_dir, jdoc)
            loaded_jsondoc = json.load(open(filepath, 'r'))
            # Synthesize a title if not present
            if 'title' not in loaded_jsondoc:
                loaded_jsondoc['title'] = filename.replace('_', ' ').title()
            # This is the filename, sans extension, for the schema document
            if '_filename' not in loaded_jsondoc:
                loaded_jsondoc['_filename'] = filename
            schema = JSONSchemaBaseObject(**loaded_jsondoc).to_jsonschema()
            schemas[filename] = schema
    return schemas

def build_templates():
    """Discover, render, and return Jinja-templated schema definitions"""
    schemas = dict()
    return schemas
