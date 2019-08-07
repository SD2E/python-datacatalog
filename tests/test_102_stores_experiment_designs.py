import pytest
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog import linkedstores
from datacatalog.linkedstores.experiment_design import ExperimentDesignStore
from .data import experiment_design

def test_exp_db_init(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    assert base is not None

def test_exp_db_heritable_schema(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    assert 'experiment_design_id' in base.get_indexes()
    assert 'title' not in base.get_indexes()

def test_exp_schema(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_exp_name(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    assert base.name == 'experiment_designs'

def test_exp_uuid_tytpe(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    assert base.get_uuid_type() == 'experiment_design'

def test_exp_issue_uuid(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    identifier_string = 'MILLER_UREY_REDUX'
    identifier_string_uuid = base.get_typeduuid(identifier_string, binary=False)
    assert identifier_string_uuid == '11439d1c-3068-57f5-9b1d-4f61a97eefa7'

def test_exp_add(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    for key, doc, uuid_val in experiment_design.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

def test_exp_update(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    for key, doc, uuid_val in experiment_design.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

@pytest.mark.delete
def test_exp_delete(mongodb_settings):
    base = ExperimentDesignStore(mongodb_settings)
    for key, doc, uuid_val in experiment_design.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
