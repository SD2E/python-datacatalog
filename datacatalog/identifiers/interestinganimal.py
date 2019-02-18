
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *

import arrow
import petname
import os

__all__ = ["generate", "mock", "validate", "pet_name"]

def generate(timestamp=True):
    pet = petname.Generate(2, '-', 8)
    if timestamp is True:
        pet = pet + arrow.utcnow().format('YYYYMMDDTHHmmss') + 'Z'
    return pet

def mock(timestamp=True):
    return generate(timestamp)

def validate(timestamp=True, permissive=False):
    raise NotImplementedError()

def pet_name(*args):
    return petname.Generate(*args)
