
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import datetime
import json
import uuid
import arrow
import importlib
import inspect

from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE
from jsonschema import validate, RefResolver

SCHEMA_FILE = '/schemas/default.jsonschema'

def current_time():
    """Current UTC time
    Returns:
        A ``datetime`` object rounded to millisecond precision
    """
    return datetime.datetime.fromtimestamp(int(datetime.datetime.utcnow().timestamp() * 1000) / 1000)

def msec_precision(datetimeval):
    dt = arrow.get(datetimeval)
    dts = dt.timestamp
    dtsp = ((dts * 1000) / 1000)
    return datetime.datetime.fromtimestamp(dtsp)


def time_stamp(dt=None, rounded=False):
    """Get time in seconds
    Args:
        dt (datetime): Optional datetime object. [current_time()]
        rounded (bool): Whether to round respose to nearest int
    Returns:
        Time expressed as a ``float`` (or ``int``)
    """
    if dt is None:
        dt = current_time()
    if rounded:
        return int(dt.timestamp())
    else:
        return dt.timestamp()

def text_uuid_to_binary(text_uuid):
    try:
        return Binary(uuid.UUID(text_uuid).bytes, OLD_UUID_SUBTYPE)
    except Exception as exc:
        raise ValueError('Failed to convert text UUID to binary', exc)

def validate_file_to_schema(filename, schema_file=SCHEMA_FILE, permissive=False):
    """Validate a JSON document against a specified JSON schema

    Args:
    filename (str): path to the file to validate
    schema_file (str): path to the requisite JSON schema file [/schemas/default.jsonschema]
    permissive (bool): swallow validation errors and return only boolean [False]

    Returns:
        Boolean value
    Error handling:
        Raises validation exceptions if 'permssive' is False.
    """
    try:
        with open(filename) as object_file:
            object_json = json.loads(object_file.read())

        with open(schema_file) as schema:
            schema_json = json.loads(schema.read())
            schema_abs = 'file://' + schema_file
    except Exception as e:
        raise Exception("file or schema loading error", e)

    class fixResolver(RefResolver):
        def __init__(self):
            RefResolver.__init__(self, base_uri=schema_abs, referrer=None)
            self.store[schema_abs] = schema_json

    try:
        validate(object_json, schema_json, resolver=fixResolver())
        return True
    except Exception as e:
        if permissive is False:
            raise Exception("file validation failed", e)
        else:
            return False

def dynamic_import(module, package=None):
    """Dynamically import a module by name at runtime

    Args:
        module (str): The name of the module to import
        package (str, optional): The package to import ``module`` from

    Returns:
        object: The imported module
    """
    return importlib.import_module(module, package=package)
