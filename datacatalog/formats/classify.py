import os
import sys
import importlib
import inspect
import itertools

from pprint import pprint
from . import *
from .converter import Converter, ConversionError

FORMATS = ['Transcriptic', 'Ginkgo', 'Biofab']

def dynamic_import(module, package=None):
    return importlib.import_module(module, package=package)

class NoClassifierError(ConversionError):
    pass

def get_converters(options={}):
    matches = list()
    for pkg in FORMATS:
        converter = globals()[pkg](options)
        matches.append(converter)
    return matches

def get_converter(json_filepath, options={}, expect=None):
    exceptions = list()
    if expect is None:
        converters = get_converters(options)
    else:
        converters = [globals()[expect](options)]

    for conv in converters:
        try:
            conv.validate_input(json_filepath)
            return conv
        except Exception as exc:
            exceptions.append(exc)

    raise NoClassifierError(
        'Classification failed for {}: {}'.format(
            os.path.basename(json_filepath), exceptions))


def _get_converter(json_filepath, options={}):

    try:
        t = Transcriptic(options=options)
        t.validate_input(json_filepath)
        return t
    except Exception as exc:
        exceptions.append(exc)

    try:
        g = Ginkgo(options=options)
        g.validate_input(json_filepath)
        return g
    except Exception as exc:
        exceptions.append(exc)

    try:
        b = Biofab(options=options)
        b.validate_input(json_filepath)
        return b
    except Exception as exc:
        exceptions.append(exc)

    raise NoClassifierError(
        'Classification failed for {}: {}'.format(
            json_filepath, exceptions))
