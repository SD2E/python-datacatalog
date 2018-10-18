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
from data import basestore

sys.path.insert(0, '/')
import datacatalog

def test_basestore_db(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)

def test_basestore_db_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)
    assert base.db.collection_names() is not None

def test_basestore_schema(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_basestore_name(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)
    assert base.name == 'basestores'

def test_basestore_issue_uuid(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)
    identifier_string = 'abcdef'
    identifier_string_uuid = base.get_typed_uuid(identifier_string, binary=False)
    assert identifier_string_uuid == '100a955e-5874-50f0-afac-e2857bc0a764'

def test_basestore_add(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)
    for key, doc, uuid_val in basestore.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] == uuid_val

def test_basestore_update(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)
    for key, doc, uuid_val in basestore.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

def test_basestore_delete(mongodb_settings):
    base = datacatalog.linkedstores.basestore.BaseStore(mongodb_settings)
    for key, doc, uuid_val in basestore.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp == {'n': 1, 'ok': 1.0}
