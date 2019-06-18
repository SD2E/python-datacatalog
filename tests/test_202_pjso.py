import abc
import os
import pytest
import sys
import yaml
import time
import warnings
import json

from pprint import pprint
from . import longrun, delete, networked
from .fixtures.mongodb import mongodb_settings, mongodb_authn

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/pjso')

from datacatalog.jsonschemas import objects
from datacatalog.managers.common import Manager

def test_pjso_can_load():
    """Smoke test to verify that the module can be loaded
    """
    assert objects.AVAILABLE is True

@pytest.mark.parametrize("title,classname", [
    ('TACC API', 'TaccApi'),
    ('TapisFiles', 'Tapisfiles'),
    ('TACC_API', 'TaccApi')])
def test_pjso_standardize_classname(title, classname):
    """Test conversion of schema title to PJSO-formatted class name
    """
    assert objects.pjso.classname_from_long_title(title) == classname


def test_pjso_cache_dir_default():
    """Test passing no value still returns a cache path
    """
    assert '.pjs-cache' in objects.pjso.__cache_path()

def test_pjso_cache_dir_override():
    """Test override cache directory
    """
    assert objects.pjso.__cache_path(
        '/home/taco/.pjs-cache') == '/home/taco/.pjs-cache'


@pytest.mark.parametrize("filename,classname,success", [
    ('person.json', 'Person', True)])
def test_pjso_from_file_no_cache(filename, classname, success):
    schema_file = os.path.join(DATA_DIR, filename)
    cobj = objects.get_class_object_from_file(schema_file, use_cache=False)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__title__ == classname

@pytest.mark.parametrize("filename,classname,success", [
    ('person.json', 'Person', True)])
def test_pjso_from_file_use_cache(filename, classname, success):
    schema_file = os.path.join(DATA_DIR, filename)
    cobj = objects.get_class_object_from_file(schema_file, use_cache=True)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__title__ == classname


@pytest.mark.parametrize("uri,classname,success", [
    ('https://raw.githubusercontent.com/json-schema-org/json-schema-org.github.io/master/learn/examples/geographical-location.schema.json', 'longitude_and_latitude_values', True),
    ('https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/gitlab-ci.json', 'gitlab_ci_configuration', True)])
def test_pjso_from_uri_no_cache(uri, classname, success):
    cobj = objects.get_class_object_from_uri(uri, use_cache=False)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__name__ == classname.lower()

@pytest.mark.parametrize("uri,classname,success", [
    ('https://raw.githubusercontent.com/json-schema-org/json-schema-org.github.io/master/learn/examples/geographical-location.schema.json', 'longitude_and_latitude_values', True),
    ('https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/gitlab-ci.json', 'gitlab_ci_configuration', True)])
def test_pjso_from_uri_use_cache(uri, classname, success):
    cobj = objects.get_class_object_from_uri(uri, use_cache=True)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__name__ == classname.lower()

@pytest.mark.parametrize("uri,classname,success", [
    ('https://raw.githubusercontent.com/json-schema-org/json-schema-org.github.io/master/learn/examples/geographical-location.schema.json', 'longitude_and_latitude_values', True),
    ('https://schema.catalog.sd2e.org/schemas/challenge_problem.json', 'challengeproblem', True),
    ('https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/gitlab-ci.json', 'gitlab_ci_configuration', True)])
def test_pjso_uri_with_cache_is_faster(uri, classname, success):
    t1 = time.time()
    objects.get_class_object_from_uri(uri, use_cache=False)
    t2 = time.time()
    objects.get_class_object_from_uri(uri, use_cache=True)
    t3 = time.time()
    objects.get_class_object_from_uri(uri, use_cache=True)
    t4 = time.time()
    wo_cache = (t2 - t1)
    wi_cache = (t4 - t3)
    if (wo_cache / wi_cache) <= objects.pjso.PJS_SLOW_CACHE_WARN_THRESHOLD:
        raise IOError(
            'Cache did not speed things up ({} vs {} sec)'.format(wo_cache, wi_cache))

# @longrun
def test_pjso_linkedstore_classes(mongodb_settings):
    from python_jsonschema_objects.validators import ValidationError
    mgr = Manager(mongodb_settings)
    assert isinstance(mgr.stores, dict)
    for store_name in list(mgr.stores.keys()):
        schema_dict = mgr.stores[store_name].schema
        try:
            cobj = objects.get_class_object_from_dict(schema_dict, use_cache=True)
            assert type(cobj) is abc.ABCMeta
        except ValidationError as verr:
            warnings.warn(
                'Validation Error loading {}: {}'.format(
                    store_name, str(verr)))
        except NotImplementedError as nierr:
            warnings.warn(
                'Unsupported JSONschema Feature in {}: {}'.format(
                    store_name, str(nierr)))
