import os
import sys
import itertools

from pprint import pprint
from . import *
from .converter import Converter, ConversionError
from ..utils import dynamic_import

FORMATS = ['Transcriptic', 'Ginkgo', 'Biofab', 'SampleAttributes']
"""Class names for document types that can be converted to Data Catalog records"""

class NoClassifierError(ConversionError):
    """Unable to classify a document, preventing its conversion"""
    pass

def get_converters(options={}):
    """Discover and return Converters

    Returns:
        list: One or more ``Converter`` objects
    """
    matches = list()
    for pkg in FORMATS:
        converter = globals()[pkg](options)
        matches.append(converter)
    return matches

def get_converter(json_filepath, options={}, expect=None):
    """Given a JSON document get the appropriate ``Converter``

    Args:
        json_filepath: Path to a file

    Raises:
        NoClassifierError: No converter could be materialized

    Returns:
        Converter: A typed instance of Converter that can transform a JSON file
    """
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
