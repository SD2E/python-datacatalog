import re

from ..schemas import IdentifierSchema, JSONSchemaCollection
from .uuidtypes import UUIDType

EXPORTED_UUID_TYPES = ('JOB', 'FILE', 'METADATA', 'NOTIFICATION')

def get_schemas():
    schemas = dict()
    for t in EXPORTED_UUID_TYPES:
        name = t.lower()
        fname = 'agave_' + name + '_uuid'
        suffix = UUIDType[t]
        doc = {'_filename': fname,
               'description': 'Agave API {} UUID'.format(name),
               'type': 'string',
               'pattern': '-{}$'.format(suffix)}
        sch = IdentifierSchema(**doc).to_jsonschema()
        schemas[fname] = sch
    return JSONSchemaCollection(schemas)
