import os
import pytest
import sys
import yaml
import json

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
from fixtures.mongodb import mongodb_settings, mongodb_authn
from data import file

sys.path.insert(0, '/')
import datacatalog

def test_get_allschema_filter_all():
    schemas = datacatalog.jsonschemas.get_all_schemas(filters=['will-never-be-valid'])
    assert isinstance(schemas, dict)
    assert len(list(schemas.keys())) == 0

def test_get_allschema_filter_one():
    schemas = datacatalog.jsonschemas.get_all_schemas(filters=['linkedstores.basestore'])
    assert isinstance(schemas, dict)
    # the object and document schemas
    assert len(list(schemas.keys())) == 2

def test_get_all_schemas():
    schemas = datacatalog.jsonschemas.get_all_schemas()
    assert isinstance(schemas, dict)
    assert len(list(schemas.keys())) > 0
