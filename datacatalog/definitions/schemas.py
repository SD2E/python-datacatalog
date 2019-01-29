import json
import os
import sys
from ..jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection

HERE = os.path.abspath(__file__)
PARENT = os.path.dirname(HERE)

class Definition(JSONSchemaBaseObject):
    pass

def get_schemas():
    """Return all definition sub-schema(s)

    Returns:
        JSONSchemaCollection: One or more schemas
    """
    jsondocs = build_jsondocs()
    templated_jsondocs = build_templates()
    schemas = JSONSchemaCollection({**jsondocs, **templated_jsondocs})
    return schemas

def build_jsondocs(directory=None):
    """Discover and return schema definitions

    Args:
        directory (str, optional): Path to JSON documents

    Raises:
        OSError: Raised when specified directory is inaccessible or nonexistent

    Returns:
        dict: Nested dictionary of schemas, keyed by filename
    """
    schemas = dict()
    if directory is None:
        docs_dir = os.path.join(PARENT, 'jsondocs')
    else:
        docs_dir = directory
        if not os.path.isdir(docs_dir):
            raise OSError('{} does not appear to exist'.format(docs_dir))
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
            if 'enum' in loaded_jsondoc:
                if len(loaded_jsondoc['enum']) > 0:
                    loaded_jsondoc['examples'] = loaded_jsondoc['enum']
            schema = Definition(**loaded_jsondoc).to_jsonschema()
            schemas[filename] = schema
    return schemas

def build_templates():
    """Discover, render, and return Jinja-templated schema definitions"""
    schemas = dict()
    return schemas
