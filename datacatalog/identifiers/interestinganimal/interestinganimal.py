import arrow
import petname
import os
from datacatalog import settings
from .examples import EXAMPLES
from ..schemas import IdentifierSchema, JSONSchemaCollection

PROPERTIES = {'id': 'interesting_animal',
              'title': 'Pet name identifier',
              'description': 'Identifier comprised of an adjective and animal name (with optional timestamp)',
              'type': 'string'}


__all__ = ["generate", "mock", "validate", "pet_name", "get_schemas"]

def generate(timestamp=True):
    pet = petname.Generate(settings.ADJ_ANIMAL_WORDS,
                           settings.ADJ_ANIMAL_DELIM,
                           settings.ADJ_ANIMAL_LENGTH)
    if timestamp is True:
        pet = pet + arrow.utcnow().format(settings.ADJ_ANIMAL_DATE_FORMAT) + 'Z'
    return pet

def mock(timestamp=True):
    return generate(timestamp)

def validate(timestamp=True, permissive=False):
    raise NotImplementedError()

def pet_name(*args):
    return petname.Generate(*args)

def get_schemas():
    schemas = dict()
    doc = {'_filename': PROPERTIES['id'],
           'description': PROPERTIES['description'],
           'type': PROPERTIES['type'],
           'examples': EXAMPLES}
    sch = IdentifierSchema(**doc).to_jsonschema()
    schemas[PROPERTIES['id']] = sch
    return JSONSchemaCollection(schemas)
