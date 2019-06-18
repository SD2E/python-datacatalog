try:
    import python_jsonschema_objects as pjs
    AVAILABLE = True
except ModuleNotFoundError:
    AVAILABLE = False

import cloudpickle
import inflection
import json
import os
import requests
import six
import time
import warnings
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from jsonschema.exceptions import RefResolutionError
from tenacity import (retry, retry_if_exception_type, stop_after_delay,
                      stop_after_attempt, wait_random)
from datacatalog import settings

PJS_CACHE_DIR = '.pjs-cache'
PJS_SLOW_CACHE_WARN_THRESHOLD = 0.95

class PjsCacheMiss(Exception):
    """Class object could not be loaded from its cache file
    """
    pass

def __normalized_classname(classname):
    return classname.title()

def classname_from_long_title(schema_title):
    # Implementation taken from python_jsonschema_objects/__init__.py#build_classes
    return inflection.camelize(inflection.parameterize(
        six.text_type(schema_title), '_'))

def name_from_long_title(schema_title):
    return inflection.parameterize(six.text_type(schema_title), '_').lower()

def title_from_schema(schema_dict):
    if 'title' in schema_dict:
        return schema_dict.get('title')
    elif '$id' in schema_dict:
        return schema_dict.get('$id')
    else:
        return schema_dict.get('id')

def __cache_path(cache_dir=None):
    cdir = '.'

    if cache_dir is None:
        cdir = os.path.join(os.path.expanduser('~'), PJS_CACHE_DIR)
    else:
        cdir = cache_dir

    __init_cache(cache_dir=cdir)
    return cdir

def __cache_filename(classname, cache_dir=None):
    return os.path.join(
        __cache_path(cache_dir), __normalized_classname(classname) + '.pickle')

def __init_cache(cache_dir=None):
    if cache_dir is None:
        cache_dir = __cache_path(cache_dir)
    try:
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    except OSError:
        return None

def __get_class_object_from_cache(classname, cache_dir=None):
    __init_cache(cache_dir)
    cfn = __cache_filename(classname, cache_dir=cache_dir)
    try:

        if not os.path.exists(cfn):
            raise PjsCacheMiss('Cache file not present')
            warnings.warn('Cache {} absent'.format(classname))

        file_age = time.time() - os.path.getmtime(cfn)
        if file_age > settings.PJS_CACHE_MAX_AGE:
            raise PjsCacheMiss('Cache file found but was too old')
            warnings.warn('Cache {} expired'.format(classname))

        cache_file = open(cfn, 'rb')
        try:
            classobj = cloudpickle.load(cache_file)
            return classobj
        except Exception:
            raise PjsCacheMiss('Cache file not loadable')
    except Exception:
        raise

def __write_class_object_to_cache(classobj, classname, cache_dir=None):
    __init_cache(cache_dir)
    cfn = __cache_filename(classname, cache_dir=cache_dir)

    cache_file = open(cfn, 'wb')
    cloudpickle.dump(classobj, cache_file)
    cache_file.close()
    return True

def get_class_object(schema_dict, classname=None, use_cache=True):
    return get_class_object_from_dict(
        schema_dict, classname=classname, use_cache=use_cache)

def get_class_object_from_dict(schema, classname=None,
                               cache_dir=None, use_cache=True):
    """Instantiate a Python class from a dict

    Args:
        schema (dict): A dict containing a JSON schema document
        classname (str, optional): Name of the instantiated class to return.
            Optional if only one class is defined by the schema document.

    Returns:
        class: A Python class named after and defined by the schema document
    """

    if not AVAILABLE:
        raise NotImplementedError(
            'The "python-jsonschema-objects" module is not available')

    if classname is None:
        actual_classname = classname_from_long_title(schema.get('title'))
    else:
        actual_classname = classname

    if use_cache:
        try:
            return __get_class_object_from_cache(
                actual_classname, cache_dir=cache_dir)
        except PjsCacheMiss:
            pass

    builder = pjs.ObjectBuilder(schema)
    ns = builder.build_classes(named_only=True, strict=True)
    try:
        clsobj = getattr(ns, actual_classname)
        try:
            if use_cache:
                __write_class_object_to_cache(
                    clsobj, actual_classname, cache_dir=cache_dir)
        except Exception:
            warnings.warn(
                'Failed to write {} to JsonschemaClassObjects cache')
        return clsobj
    except AttributeError:
        raise ValueError(
            'No class {} was found. Currently known options are {}'.format(
                classname,
                ', '.join(dir(ns))))

def get_class_object_from_file(schema_file, classname=None, use_cache=True):
    """Instantiate a Python class object from a JSONschema file

    Args:
        schema_file (str): Path to a file holding a JSONschema document
        classname (str, optional): Name of the instantiated class to return.
            Optional if only one class is defined by the schema document.

    Returns:
        class: A Python class named after and defined by the schema
    """
    schema_dict = json.load(open(schema_file, 'r'))
    actual_classname = classname_from_long_title(
        title_from_schema(schema_dict))
    return get_class_object_from_dict(
        schema_dict, classname=actual_classname, use_cache=use_cache)

@retry(retry=retry_if_exception_type(RefResolutionError), stop=(stop_after_delay(15) | stop_after_attempt(5)), wait=wait_random(min=1, max=3), reraise=True)
def get_class_object_from_uri(schema_uri, classname=None, use_cache=True):
    """Instantiate a Python class object from a JSONschema URI

    Args:
        schema_uri (str): URI for a JSONschema document
        classname (str, optional): Name of the instantiated class to return.
            Optional if only one class is defined by the schema document.

    Returns:
        class: A Python class named after and defined by the schema
    """
    resp = requests.get(schema_uri, allow_redirects=True, timeout=1)
    resp.raise_for_status()
    schema_dict = resp.json()
    actual_classname = classname_from_long_title(
        title_from_schema(schema_dict))
    return get_class_object_from_dict(
        schema_dict, classname=actual_classname, use_cache=use_cache)
