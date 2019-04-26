import re

from ..schemas import IdentifierSchema, JSONSchemaCollection
from .examples import AGAVE_METADATA_UUID as EXAMPLES
from .uuidtypes import UUIDType

EXPORTED_UUID_TYPES = ('JOB', 'FILE', 'METADATA', 'NOTIFICATION', 'APP', 'SYSTEM')

def get_schemas():
    schemas = dict()
    for t in EXPORTED_UUID_TYPES:
        name = t.lower()
        fname = 'agave_' + name + '_uuid'
        suffix = UUIDType[t]
        filtered_examples = [ex for ex in EXAMPLES if ex.endswith(suffix)]
        doc = {'_filename': fname,
               'description': 'Agave API {} UUID'.format(name),
               'type': 'string',
               'pattern': '-{}$'.format(suffix),
               'examples': filtered_examples}
        sch = IdentifierSchema(**doc).to_jsonschema()
        schemas[fname] = sch
    return JSONSchemaCollection(schemas)
