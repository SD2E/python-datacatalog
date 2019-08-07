import pytest
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog import linkedstores
from datacatalog.linkedstores.sample import SampleStore
from .data import sample

def test_samp_db_init(mongodb_settings):
    base = SampleStore(mongodb_settings)

def test_samp_db_heritable_schema(mongodb_settings):
    base = SampleStore(mongodb_settings)
    assert 'contents' in base.get_indexes()
    assert 'title' not in base.get_indexes()

def test_samp_db_list_collection_names(mongodb_settings):
    base = SampleStore(mongodb_settings)
    assert base.db.list_collection_names() is not None

def test_samp_schema(mongodb_settings):
    base = SampleStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_samp_name(mongodb_settings):
    base = SampleStore(mongodb_settings)
    assert base.name == 'samples'

def test_samp_uuid_tytpe(mongodb_settings):
    base = SampleStore(mongodb_settings)
    assert base.get_uuid_type() == 'sample'

def test_samp_issue_uuid(mongodb_settings):
    base = SampleStore(mongodb_settings)
    identifier_string = 'emerald.sample.unrepresentative-sample'
    identifier_string_uuid = base.get_typeduuid(identifier_string, binary=False)
    assert identifier_string_uuid == '10382668-9f1c-591d-b9f3-fca72a191225'

def test_samp_add(mongodb_settings):
    base = SampleStore(mongodb_settings)
    for key, doc, uuid_val in sample.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

def test_samp_update(mongodb_settings):
    base = SampleStore(mongodb_settings)
    for key, doc, uuid_val in sample.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

@pytest.mark.delete
def test_samp_delete(mongodb_settings):
    base = SampleStore(mongodb_settings)
    for key, doc, uuid_val in sample.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
