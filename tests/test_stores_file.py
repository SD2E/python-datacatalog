import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
from .data import file

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
        assert '_update_token' in resp

def test_files_update(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val, strategy='merge')
        assert resp['uuid'] == uuid_val
        assert '_update_token' in resp

def test_files_get_links(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        links = base.get_links(uuid_val, 'child_of')
        assert isinstance(links, list)

def test_files_remove_linkage(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.remove_link(uuid_val, '1040f664-54a6-0b71-8941-277a05ac6fa7')
        assert '1040f664-54a6-0b71-8941-277a05ac6fa7' not in resp.get('child_of', dict)

def test_files_add_linkage(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_link(uuid_val, '1040f664-a654-0b71-4189-2ac6f77a05a7')
        assert '1040f664-a654-0b71-4189-2ac6f77a05a7' in resp.get('child_of', dict)
        links = base.get_links(uuid_val, 'child_of')
        assert '1040f664-a654-0b71-4189-2ac6f77a05a7' in links

def test_files_replace(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.REPLACES:
        resp = base.add_update_document(doc, uuid=uuid_val, strategy='replace')
        assert resp['uuid'] == uuid_val
        assert '_update_token' in resp
        links = base.get_links(uuid_val, 'child_of')
        assert len(links) == len(doc.get('child_of', list()))

@delete
def test_files_delete(mongodb_settings):
    base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
    for key, doc, uuid_val in file.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
