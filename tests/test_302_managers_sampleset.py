import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures import mongodb_settings, mongodb_authn
import datacatalog
from .data import challenge_problem, experiment

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/sampleset')

@pytest.fixture(scope='session')
def samplesetprocessor(mongodb_settings):
    return datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings)

def test_inspect_discover_stores(mongodb_settings):
    base = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings)

    # stores is a dict of store objected indexed by name
    assert isinstance(base.stores, dict)
    assert len(list(base.stores.keys())) > 0

    # check that they all have schemas
    for k, v in base.stores.items():
        assert isinstance(v.schema, dict)

def test_cp_get(samplesetprocessor):
    for key, doc, uuid_val in challenge_problem.CREATES:
        samplesetprocessor.stores['challenge_problem'].add_update_document(doc)
        resp = samplesetprocessor.get('challenge_problem', 'id', doc['id'])
        assert resp['id'] == doc['id']

def test_ex_get(samplesetprocessor):
    for key, doc, uuid_val in experiment.CREATES:
        samplesetprocessor.stores['experiment'].add_update_document(doc)
        resp = samplesetprocessor.get('experiment', 'experiment_id', doc['experiment_id'])
        assert resp['experiment_id'] == doc['experiment_id']

@longrun
@pytest.mark.parametrize("filename", ['samples-biofab.json', 'samples-transcriptic.json', 'samples-ginkgo.json'])
def test_iter_process_merge(mongodb_settings, filename):
    jsonpath = os.path.join(DATA_DIR, filename)
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
    dbp = db.process(strategy='merge')
    assert dbp is True

# def test_iter_process_replace(mongodb_settings):
#     jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
#     db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
#     dbp = db.process(strategy='replace')
#     assert dbp is True

# def test_iter_process_drop(mongodb_settings):
#     jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
#     db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
#     dbp = db.process(strategy='drop')
#     assert dbp is True
