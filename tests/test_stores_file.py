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

def test_files_db(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)

def test_files_db_list_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    assert base.db.list_collection_names() is not None

def test_files_schema(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_files_name(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    assert base.name == 'files'

def test_files_uuid_tytpe(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    assert base.get_uuid_type() == 'file'

def test_files_issue_uuid(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    filename = 'science-results.xlsx'
    identifier_string_uuid = base.get_typed_uuid(filename, binary=False)
    assert identifier_string_uuid == '1059e14b-a341-5804-ac69-5c731f6ecf80'

def test_files_add(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

def test_files_update(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

def test_files_delete(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
