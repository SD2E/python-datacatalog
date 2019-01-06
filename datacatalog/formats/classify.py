import os
import sys
import importlib
import inspect
import itertools
import magic

from pprint import pprint
from . import *
from .converter import Converter, ConversionError

FORMATS = ['Transcriptic', 'Ginkgo', 'Biofab', 'SampleAttributes']

def dynamic_import(module, package=None):
    return importlib.import_module(module, package=package)

class NoClassifierError(ConversionError):
    pass

def get_converters(options={}):
    matches = list()
    for pkg in FORMATS:
        converter = globals()[pkg](options=options)
        matches.append(converter)
    return matches

def get_converter(json_filepath, options={}, expect=None):
    exceptions = list()
    if expect is None:
        converters = get_converters(options)
    else:
        converters = [globals()[expect](options)]

    encoding = magic.from_file(json_filepath)

    if encoding == "UTF-8 Unicode text":
        encoding = "utf-8"
    elif encoding == "ASCII text":
        encoding = "ascii"
    elif encoding == "ASCII text, with very long lines, with no line terminators":
        encoding = "ascii"
    else:
        raise ValueError("Unknown encoding: {}".format(encoding))

    print("Detected encoding {}".format(encoding))
    for conv in converters:
        try:
            conv.validate_input(json_filepath, encoding)
            return conv
        except Exception as exc:
            exceptions.append(exc)

    raise NoClassifierError(
        'Classification failed for {}: {}'.format(
            os.path.basename(json_filepath), exceptions))
