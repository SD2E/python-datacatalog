import os
import pytest
import json

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog.linkedstores.process import ProcessStore
from .data import process

def test_procs_db_init(mongodb_settings):
    base = ProcessStore(mongodb_settings)
    assert base is not None

def test_procs_uuid_tytpe(mongodb_settings):
    base = ProcessStore(mongodb_settings)
    assert base.get_uuid_type() == 'process'

def test_procs_issue_uuid(mongodb_settings):
    base = ProcessStore(mongodb_settings)
    process_name = 'pytest-tests'
    identifier_string_uuid = base.get_typeduuid(process_name, binary=False)
    assert identifier_string_uuid == '11720269-661b-5454-aa46-c90579d58cf2'

def test_procs_add(mongodb_settings):
    base = ProcessStore(mongodb_settings)
    for uuid, doc in process.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] == uuid

@pytest.mark.delete
def test_procs_delete(mongodb_settings):
    base = ProcessStore(mongodb_settings)
    for uuid, doc in process.DELETES:
        resp = base.delete_document(uuid)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
