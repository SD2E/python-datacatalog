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

def test_samp_clean(mongodb_settings):
    base = SampleStore(mongodb_settings)
    for key, doc, uuid_val in sample.CLEAN:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

    assert "control_type" in base.query({"sample_id" : "sample1.lab.experiment.lab.4"})[0]
    assert "standard_type" in base.query({"sample_id" : "sample1.lab.experiment.lab.4"})[0]
    assert "control_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.4"})[0]
    assert "standard_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.4"})[0]
    assert "control_type" not in base.query({"sample_id" : "sample1.lab.experiment.lab.5"})[0]
    assert "standard_type" not in base.query({"sample_id" : "sample1.lab.experiment.lab.5"})[0]
    assert "control_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.5"})[0]
    assert "standard_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.5"})[0]

    update_result = base.clean_fields("experiment.lab.4", ["control_type", "standard_type"])
    assert(update_result.matched_count == 2)
    assert(update_result.modified_count == 1)

    # should be removed from sample1.lab.experiment.lab.4
    assert "control_type" not in base.query({"sample_id" : "sample1.lab.experiment.lab.4"})[0]
    assert "standard_type" not in base.query({"sample_id" : "sample1.lab.experiment.lab.4"})[0]
    assert "control_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.4"})[0]
    assert "standard_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.4"})[0]
    assert "control_type" not in base.query({"sample_id" : "sample1.lab.experiment.lab.5"})[0]
    assert "standard_type" not in base.query({"sample_id" : "sample1.lab.experiment.lab.5"})[0]
    assert "control_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.5"})[0]
    assert "standard_type" not in base.query({"sample_id" : "sample2.lab.experiment.lab.5"})[0]

    # no effect on experiment without fields
    update_result = base.clean_fields("experiment.lab.5", ["control_type", "standard_type"])
    assert(update_result.matched_count == 2)
    assert(update_result.modified_count == 0)

    # no effect on previously cleaned experiment
    update_result = base.clean_fields("experiment.lab.4", ["control_type", "standard_type"])
    assert(update_result.matched_count == 2)
    assert(update_result.modified_count == 0)

    # no effect on non-matching experiment
    update_result = base.clean_fields("experiment.lab.foo1", ["control_type", "standard_type"])
    assert(update_result.matched_count == 0)
    assert(update_result.modified_count == 0)

def test_samp_clean_fail(mongodb_settings):
    base = SampleStore(mongodb_settings)
    for key, doc, uuid_val in sample.CLEAN:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

    with pytest.raises(ValueError, match="Must specify at least one field to clean"):
        update_result = base.clean_fields("experiment.lab.foo", [])

    with pytest.raises(ValueError, match="Experiment id is not namespaced 'invalid_exp'"):
        update_result = base.clean_fields("invalid_exp", ["control_type", "standard_type"])

    with pytest.raises(ValueError, match="Field to clean is not declared 'invalid_field'"):
        update_result = base.clean_fields("experiment.lab.foo", ["invalid_field"])

    with pytest.raises(ValueError, match="Field to clean is a token field 'uuid'"):
        update_result = base.clean_fields("experiment.lab.foo", ["uuid"])

    with pytest.raises(ValueError, match="Field to clean is a uuid field 'sample_id'"):
        update_result = base.clean_fields("experiment.lab.foo", ["sample_id"])

    with pytest.raises(ValueError, match="Field to clean is a read only field '_salt'"):
        update_result = base.clean_fields("experiment.lab.foo", ["_salt"])

    with pytest.raises(ValueError, match="Field to clean is required 'measurements'"):
        update_result = base.clean_fields("experiment.lab.foo", ["measurements"])

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
