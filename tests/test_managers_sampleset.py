import os
import pytest
import sys
import yaml
import json
import types

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/sampleset')

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
from fixtures.mongodb import mongodb_settings, mongodb_authn
from data import challenge_problem, experiment

sys.path.insert(0, '/')
import datacatalog

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
        resp = samplesetprocessor.get('experiment', 'id', doc['id'])
        assert resp['id'] == doc['id']

def test_cpid_get_from_doc(mongodb_settings):
    jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
    cp = db.get_challenge_problem_id()
    assert cp == 'YEAST_GATES'

def test_exid_get_from_doc(mongodb_settings):
    jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
    ex = db.get_experiment_id()
    assert ex == 'NovelChassis-NAND-Gate'

# def test_iter_samples(mongodb_settings):
#     jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
#     db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
#     x = db.samples()
#     assert isinstance(x, types.GeneratorType)

# def test_iter_meas(mongodb_settings):
#     jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
#     db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
#     x = db.samples()
#     y = db.measurements(x)
#     assert isinstance(y, types.GeneratorType)

# def test_iter_file(mongodb_settings):
#     jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
#     db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
#     x = db.samples()
#     y = db.measurements(x)
#     z = db.files(y)
#     assert isinstance(z, types.GeneratorType)

def test_iter_process(mongodb_settings):
    jsonpath = os.path.join(DATA_DIR, 'samples-biofab.json')
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, jsonpath)
    dbp = db.process()
    assert dbp is True
