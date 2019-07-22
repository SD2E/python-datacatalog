import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures import mongodb_settings, mongodb_authn, agave, credentials
import datacatalog
from .data import challenge_problem, experiment
from datacatalog.linkedstores.basestore.diff import get_diff, diff_list

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
    ssp = samplesetprocessor
    for key, doc, uuid_val in challenge_problem.CREATES:
        ssp.stores['challenge_problem'].add_update_document(doc)
        resp = ssp.get('challenge_problem', 'id', doc['id'])
        assert resp['id'] == doc['id']

def test_ex_get(samplesetprocessor):
    for key, doc, uuid_val in experiment.CREATES:
        samplesetprocessor.stores['experiment'].add_update_document(doc)
        resp = samplesetprocessor.get('experiment', 'experiment_id', doc['experiment_id'])
        assert resp['experiment_id'] == doc['experiment_id']

@pytest.mark.parametrize("samples_uri", [
    'agave://data-sd2e-projects.sd2e-project-21/ReedM-index/A_eq_B/20190214_A_eq_B_mar_1/20190214-A-B-mar-1.json', 'agave://data-sd2e-community/sample/tacc-cloud/sampleset/samples_nc.json'])
def test_init_setup_no_agave(mongodb_settings, samples_uri):
    with pytest.raises(Exception):
        db = datacatalog.managers.sampleset.SampleSetProcessor(
            mongodb_settings,
            agave=None,
            samples_uri=samples_uri).setup()
        assert db is not None

@pytest.mark.parametrize("samples_uri", [
    'agave://data-sd2e-projects.sd2e-project-21/ReedM-index/A_eq_B/20190214_A_eq_B_mar_1/20190214-A-B-mar-1.json', 'agave://data-sd2e-community/sample/tacc-cloud/sampleset/samples_nc.json'])
def test_init_setup(mongodb_settings, agave, samples_uri):
    db = datacatalog.managers.sampleset.SampleSetProcessor(
        mongodb_settings,
        agave=agave,
        samples_uri=samples_uri).setup()
    assert db is not None

@pytest.mark.parametrize("samples_uri", [
    'agave://data-sd2e-projects.sd2e-project-21/ReedM-index/A_eq_B/20190214_A_eq_B_mar_1/20190214-A-B-mar-1.json', 'agave://data-sd2e-community/sample/tacc-cloud/sampleset/samples_nc.json'])
def test_init_setup_prefix(mongodb_settings, agave, samples_uri):
    ag_sys, ag_path, ag_file = datacatalog.agavehelpers.from_agave_uri(samples_uri)
    db = datacatalog.managers.sampleset.SampleSetProcessor(
        mongodb_settings,
        agave=agave,
        samples_uri=samples_uri,
        path_prefix=ag_path).setup()
    assert db is not None

# @pytest.mark.parametrize("samples_uri", [
#     'agave://data-sd2e-projects.sd2e-project-21/ReedM-index/A_eq_B/20190214_A_eq_B_mar_1/20190214-A-B-mar-1.json', 'agave://data-sd2e-community/sample/tacc-cloud/sampleset/samples_nc.json'])
# def test_init_setup_named_download(mongodb_settings, agave, samples_uri):
#     db = datacatalog.managers.sampleset.SampleSetProcessor(
#         mongodb_settings,
#         agave=agave,
#         samples_uri=samples_uri).setup()
#     assert db is not None

@longrun
@pytest.mark.parametrize("filename", ['samples-biofab-022019.json', 'samples-transcriptic-022019.json'])
def test_iter_process_merge(mongodb_settings, filename):
    jsonpath = os.path.join(DATA_DIR, filename)
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, samples_file=jsonpath).setup()
    dbp = db.process(strategy='merge')
    assert dbp is True


@longrun
@pytest.mark.parametrize("samples_uri", ['agave://data-sd2e-community/sample/tacc-cloud/sampleset/samples_nc.json'])
def test_process_from_uri_only(mongodb_settings, agave, samples_uri):
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings,
                                                           agave=agave,
                                                           samples_uri=samples_uri).setup()
    dbp = db.process(strategy='replace')
    assert dbp is True

@longrun
@pytest.mark.parametrize("filename, samples_uri", [('samples_nc.json',
                                                   'agave://data-sd2e-community/sample/tacc-cloud/sampleset/samples_nc.json')])
def test_process_from_file_w_uri(mongodb_settings, agave, filename, samples_uri):
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings,
                                                           agave=agave,
                                                           samples_file=filename,
                                                           samples_uri=samples_uri).setup()
    dbp = db.process(strategy='replace')
    assert dbp is True

@longrun
@pytest.mark.parametrize("filename", ['samples-titration.json'])
def test_titration_nan_merge(mongodb_settings, filename):
    jsonpath = os.path.join(DATA_DIR, filename)
    db = datacatalog.managers.sampleset.SampleSetProcessor(mongodb_settings, samples_file=jsonpath).setup()
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
