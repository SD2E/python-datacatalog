import pytest
import abc
import os
import time
import warnings
import json

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/pjso')

from datacatalog.jsonschemas import objects
from datacatalog.managers.common import Manager

def test_pjso_can_load():
    """Smoke test to verify the Pjs module can be loaded under the hood
    """
    assert objects.AVAILABLE is True

@pytest.mark.parametrize("title,classname", [
    ('TACC API', 'TaccApi'),
    ('TapisFiles', 'Tapisfiles'),
    ('TACC_API', 'TaccApi')])
def test_pjso_classname_from_long_title(title, classname):
    """Schema title converts to a PJSO-formatted class name
    """
    assert objects.pjso.classname_from_long_title(title) == classname


def test_pjso_cache_dir_default():
    """Passing None results in default cache path
    """
    assert '.pjs-cache' in objects.cache_directory()

def test_pjso_cache_dir_override(pjso_cache_dir):
    """Cache directory can be over-ridden
    """
    cdir = pjso_cache_dir
    assert objects.cache_directory(cdir) == cdir

@pytest.mark.parametrize("filename,classname,success", [
    ('person.json', 'Person', True)])
def test_pjso_from_file_no_cache(filename, classname, success, pjso_cache_dir):
    """JSON schema file can be turned into a Pjso class object, with
    cacheing inactive.
    """
    schema_file = os.path.join(DATA_DIR, filename)
    cobj = objects.get_class_object_from_file(schema_file, use_cache=False)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__title__ == classname

@pytest.mark.parametrize("filename,classname,success", [
    ('person.json', 'Person', True)])
def test_pjso_from_file_use_cache(filename, classname, success, pjso_cache_dir):
    """JSON schema file can be turned into a Pjso class object, with
    cacheing active.
    """
    schema_file = os.path.join(DATA_DIR, filename)
    cobj = objects.get_class_object_from_file(schema_file, use_cache=True)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__title__ == classname

def test_pjso_class_to_instance(pjso_cache_dir):
    """An instance of Person can be generated by a Pjso class object
    """
    schema_file = os.path.join(DATA_DIR, 'person.json')
    cobj = objects.get_class_object_from_file(schema_file, use_cache=True)
    instance = cobj(firstName="TACO", lastName="Cat", age=18)
    assert instance.__class__.__name__ == 'person'
    assert instance.firstName == 'TACO'
    assert instance.age == 18

def test_pjso_class_to_instance_enforce_validation(pjso_cache_dir):
    """Age is defined in the schema as a number. Thus, passing a string results
    in a ValidationError
    """
    from python_jsonschema_objects.validators import ValidationError
    schema_file = os.path.join(DATA_DIR, 'person.json')
    cobj = objects.get_class_object_from_file(schema_file, use_cache=True)
    with pytest.raises(ValidationError):
        cobj(firstName="TACO", lastName="Cat", age='18')

def test_pjso_class_to_instance_enforce_required(pjso_cache_dir):
    """Field lastName is required in the schema. Thus, attempts to create an
    instance of Person object without it must fail with a ValidationError
    """
    from python_jsonschema_objects.validators import ValidationError
    schema_file = os.path.join(DATA_DIR, 'person.json')
    cobj = objects.get_class_object_from_file(schema_file, use_cache=True)
    with pytest.raises(ValidationError):
        cobj(firstName="TACO")
    with pytest.raises(ValidationError):
        cobj(age=18)
    with pytest.raises(ValidationError):
        cobj(age=18, firstName="TACO")
    cobj(lastName="Cat")

@pytest.mark.parametrize("uri,classname,success", [
    ('https://raw.githubusercontent.com/json-schema-org/json-schema-org.github.io/master/learn/examples/geographical-location.schema.json', 'longitude_and_latitude_values', True),
    ('https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/gitlab-ci.json', 'gitlab_ci_configuration', True)])
def test_pjso_from_uri_no_cache(uri, classname, success, pjso_cache_dir):
    """Pjso class objects can be created by loading a JSONschema via HTTP with
    the cache function inactive
    """
    cobj = objects.get_class_object_from_uri(uri, use_cache=False)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__name__ == classname.lower()

@pytest.mark.parametrize("uri,classname,success", [
    ('https://raw.githubusercontent.com/json-schema-org/json-schema-org.github.io/master/learn/examples/geographical-location.schema.json', 'longitude_and_latitude_values', True),
    ('https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/gitlab-ci.json', 'gitlab_ci_configuration', True)])
def test_pjso_from_uri_use_cache(uri, classname, success, pjso_cache_dir):
    """Pjso class objects can be created by loading a JSONschema via HTTP with
    the cache function active
    """
    cobj = objects.get_class_object_from_uri(uri, use_cache=True)
    assert type(cobj) is abc.ABCMeta
    assert cobj.__name__ == classname.lower()

@pytest.mark.parametrize("uri,classname,success", [
    ('https://raw.githubusercontent.com/json-schema-org/json-schema-org.github.io/master/learn/examples/geographical-location.schema.json', 'longitude_and_latitude_values', True),
    ('https://schema.catalog.sd2e.org/schemas/challenge_problem.json', 'challengeproblem', True),
    ('https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/gitlab-ci.json', 'gitlab_ci_configuration', True)])
def test_pjso_uri_with_cache_is_faster(uri, classname, success):
    """Using the cache should always faster. Check against a defined
    tolerance for how true that should be
    """
    t1 = time.time()
    objects.get_class_object_from_uri(uri, use_cache=False)
    t2 = time.time()
    objects.get_class_object_from_uri(uri, use_cache=True)
    t3 = time.time()
    objects.get_class_object_from_uri(uri, use_cache=True)
    t4 = time.time()
    wo_cache = (t2 - t1)
    wi_cache = (t4 - t3)
    if (wo_cache / wi_cache) <= objects.SLOW_CACHE_WARN_THRESHOLD:
        raise IOError(
            'Cache did not speed things up ({} vs {} sec)'.format(wo_cache, wi_cache))

@pytest.mark.longrun
def test_pjso_linkedstore_classes(mongodb_settings, pjso_cache_dir):
    """A penultimate test for Pjso in the Data Catalog package. It must be
    possible and performant to get a Pjso class object for any LinkedStore
    that is available to managers.common.Manager or its child classes.
    """
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

@pytest.mark.delete
def test_clear_cache(pjso_cache_dir):
    objects.cache.clear_cache()
