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
from .data import experiment
from datacatalog.linkedstores.experiment import ExperimentStore

def test_exp_db_init(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    assert base is not None

def test_exp_db_heritable_schema(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    assert 'experiment_id' in base.get_indexes()
    assert 'title' not in base.get_indexes()

def test_exp_schema(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_exp_name(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    assert base.name == 'experiments'

def test_exp_uuid_tytpe(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    assert base.get_uuid_type() == 'experiment'

def test_exp_issue_uuid(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    identifier_string = 'MILLER_UREY_REDUX'
    identifier_string_uuid = base.get_typeduuid(identifier_string, binary=False)
    assert identifier_string_uuid == '10239d1c-3068-57f5-9b1d-4f61a97eefa7'

def test_exp_add(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    for key, doc, uuid_val in experiment.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

def test_exp_update(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    for key, doc, uuid_val in experiment.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

@delete
def test_exp_delete(mongodb_settings):
    base = ExperimentStore(mongodb_settings)
    for key, doc, uuid_val in experiment.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
