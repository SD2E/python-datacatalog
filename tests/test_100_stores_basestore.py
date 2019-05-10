import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete, smoketest, bootstrap

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
from .data import basestore

@bootstrap
def test_basestore_db(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()

@bootstrap
def test_basestore_db_list_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    assert base.db.list_collection_names() is not None

def test_basestore_schema(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    assert isinstance(base.schema, dict)

def test_basestore_name(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    assert base.name == 'basestores'

def test_basestore_issue_uuid(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    identifier_string = 'abcdef'
    identifier_string_uuid = base.get_typeduuid(identifier_string, binary=False)
    assert identifier_string_uuid == '100a955e-5874-50f0-afac-e2857bc0a764'

def test_basestore_add(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    for key, doc, uuid_val in basestore.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] == uuid_val
        break

def test_basestore_replace(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    for key, doc, uuid_val in basestore.REPLACES:
        resp = base.add_update_document(doc, strategy='replace')
        assert resp['replacement_works'] is True
        break

def test_basestore_update(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    for key, doc, uuid_val in basestore.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val
        break

def basestore_write_key(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    for key, doc, uuid_val in basestore.UPDATES:
        key = 'keykeykey'
        val = 'valvalval'
        resp = base.write_key(uuid_val, key, val)
        assert resp[key] == val

def basestore_delete(mongodb_settings):
    base = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    base.setup()
    for key, doc, uuid_val in basestore.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}

