import arrow
import petname
import os
from datacatalog import settings

__all__ = ["generate", "mock", "validate", "pet_name"]

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
