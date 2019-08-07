import os
import pytest
import json

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog.linkedstores.reference import ReferenceStore
from .data import reference

def test_refs_db_init(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    assert base is not None

def test_refs_uuid_tytpe(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    assert base.get_uuid_type() == 'reference'

def test_refs_issue_uuid(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    uri = 'https://www.rcsb.org/structure/6N0V'
    identifier_string_uuid = base.get_typeduuid(uri, binary=False)
    assert identifier_string_uuid == '10900dfc-0d9f-5421-8ae7-6fba4d4ed795'

def test_refs_add(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    for uuid, doc in reference.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

@pytest.mark.delete
def test_refs_delete(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    for uuid, doc in reference.DELETES:
        resp = base.delete_document(uuid)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
