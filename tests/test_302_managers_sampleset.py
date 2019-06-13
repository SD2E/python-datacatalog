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

@longrun
def test_titration_science_view_table_read(mongodb_settings):
    #  needs to run after test_titration_nan_merge above so data is available!
    # TODO add pytest dependency?
    #  ensure science_view and science_table are populating correctly
    aggs = datacatalog.views.aggregations.get_aggregations()
    assert "science_table" in aggs and "science_view" in aggs

    db = datacatalog.mongo.db_connection(mongodb_settings)

    science_table_result = db.science_table.find_one({"sample_id":"sample.ginkgo.12757493.experiment.ginkgo.19606.19637.19708.19709"})
    del science_table_result["_id"]

    science_table_expected = {
        "agave_path" : "/uploads/attachments/biotek_multi_csv/e10244/c224255.txt",
        "agave_system": "data-sd2e-community",
        "challenge_problem" : "NOVEL_CHASSIS",
        "experiment_id" : "experiment.ginkgo.19606.19637.19708.19709",
        "experiment_reference" : "NovelChassis-NAND-Ecoli-Titration",
        "experiment_reference_url" : "https://docs.google.com/document/d/1oMC5VM3XcFn6zscxLKLUe4U-TXbBsz8H6OQwHal1h4g",
        "file_type" : "PLAIN",
        "filename" : "/uploads/attachments/biotek_multi_csv/e10244/c224255.txt",
        "hpc_path" : "/work/projects/SD2E-Community/prod/data/uploads/attachments/biotek_multi_csv/e10244/c224255.txt",
        "jupyter_path" : "/home/jupyter/sd2e-community/uploads/attachments/biotek_multi_csv/e10244/c224255.txt",
        "lab" : "ginkgo",
        "level" : "0",
        "measurement_type" : "PLATE_READER",
        "reference_sample_id" : "sample.ginkgo.12726577.experiment.ginkgo.19606.19637.19708.19709",
        "replicate" : 4,
        "sample_contents" : [
            {
                "name" : {
                    "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/sigma_G8270/1",
                    "label" : "Dextrose (D-Glucose)",
                    "lab_id" : "name.ginkgo.403"
                },
                "value" : 0.399877067,
                "unit" : "%"
            },
            {
                "name" : {
                    "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/CAT_G33_500/1",
                    "label" : "Glycerol",
                    "lab_id" : "name.ginkgo.1"
                }
            },
            {
                "name" : {
                    "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/IPTG/1",
                    "label" : "IPTG",
                    "lab_id" : "name.ginkgo.376"
                },
                "value" : 0.000025000003,
                "unit" : "M"
            },
            {
                "name" : {
                    "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/Larabinose/1",
                    "label" : "L-arabinose",
                    "lab_id" : "name.ginkgo.772"
                },
                "value" : 0.02495,
                "unit" : "M"
            },
            {
                "name" : {
                    "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/Kanamycin0x20Sulfate/1",
                    "label" : "Kanamycin Sulfate",
                    "lab_id" : "name.ginkgo.394"
                },
                "value" : 7.138e-10,
                "unit" : "g/L"
            },
            {
                "name" : {
                    "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/LB_Broth/1",
                    "label" : "LB Broth (Miller)",
                    "lab_id" : "name.ginkgo.2776"
                }
            },
            {
                "name" : {
                    "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/M9_supplemented_no_carbon/1",
                    "label" : "M9_supplemented_no_carbon",
                    "lab_id" : "name.ginkgo.678"
                },
                "value" : 0.999692667,
                "unit" : "X"
            }
        ],
        "sample_id" : "sample.ginkgo.12757493.experiment.ginkgo.19606.19637.19708.19709",
        "strain" : "MG1655_empty_landing_pads",
        "strain_lab_id" : "name.ginkgo.346047",
        "strain_sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/MG1655_empty_landing_pads/1",
        "temperature" : {
            "value" : 37.0,
            "unit" : "celsius"
        },
        "timepoint" : {
            "value" : 6.5,
            "unit" : "hour"
        }
    }

    assert science_table_result == science_table_expected

    science_view_result = db.science_view.find_one({"sample.sample_id":"sample.ginkgo.12757493.experiment.ginkgo.19606.19637.19708.19709"})
    del science_view_result["_id"]
    del science_view_result["_admin"]
    del science_view_result["created"]
    del science_view_result["updated"]
    del science_view_result["uuid"]
    del science_view_result["_properties"]
    del science_view_result["_salt"]
    del science_view_result["experiment_design"]["created"]
    del science_view_result["experiment_design"]["updated"]
    for val in ["experiment_design", "experiment", "measurement", "sample", "file"]:
        del science_view_result[val]["_id"]
        del science_view_result[val]["_admin"]
        del science_view_result[val]["child_of"]
        del science_view_result[val]["_properties"]
        del science_view_result[val]["uuid"]
        del science_view_result[val]["_salt"]
        if "acted_on" in science_view_result[val]:
            del science_view_result[val]["acted_on"]
        if "acted_using" in science_view_result[val]:
            del science_view_result[val]["acted_using"]

    science_view_expected = {
        "id" : "NOVEL_CHASSIS",
        "status" : "ACTIVE",
        "title" : "Novel Chassis",
        "uri" : "https://docs.google.com/document/d/17Uy48TwzRdC1H1MLpxlfOmnQNOvk4S5Q",
        "experiment_design" : {
            "experiment_design_id" : "NovelChassis-NAND-Ecoli-Titration",
            "status" : "DRAFT",
            "title" : "CP Experimental Request - NovelChassis_NAND_Ecoli_Titration",
            "uri" : "https://docs.google.com/document/d/1oMC5VM3XcFn6zscxLKLUe4U-TXbBsz8H6OQwHal1h4g"
        },
        "experiment" : {
            "experiment_id" : "experiment.ginkgo.19606.19637.19708.19709"
        },
        "sample" : {
            "sample_id" : "sample.ginkgo.12757493.experiment.ginkgo.19606.19637.19708.19709",
            "lab_sample_id" : "sample.ginkgo.12757493",
            "contents" : [
                {
                    "name" : {
                        "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/sigma_G8270/1",
                        "label" : "Dextrose (D-Glucose)",
                        "lab_id" : "name.ginkgo.403"
                    },
                    "value" : 0.399877067,
                    "unit" : "%"
                },
                {
                    "name" : {
                        "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/CAT_G33_500/1",
                        "label" : "Glycerol",
                        "lab_id" : "name.ginkgo.1"
                    }
                },
                {
                    "name" : {
                        "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/IPTG/1",
                        "label" : "IPTG",
                        "lab_id" : "name.ginkgo.376"
                    },
                    "value" : 0.000025000003,
                    "unit" : "M"
                },
                {
                    "name" : {
                        "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/Larabinose/1",
                        "label" : "L-arabinose",
                        "lab_id" : "name.ginkgo.772"
                    },
                    "value" : 0.02495,
                    "unit" : "M"
                },
                {
                    "name" : {
                        "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/Kanamycin0x20Sulfate/1",
                        "label" : "Kanamycin Sulfate",
                        "lab_id" : "name.ginkgo.394"
                    },
                    "value" : 7.138e-10,
                    "unit" : "g/L"
                },
                {
                    "name" : {
                        "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/LB_Broth/1",
                        "label" : "LB Broth (Miller)",
                        "lab_id" : "name.ginkgo.2776"
                    }
                },
                {
                    "name" : {
                        "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/M9_supplemented_no_carbon/1",
                        "label" : "M9_supplemented_no_carbon",
                        "lab_id" : "name.ginkgo.678"
                    },
                    "value" : 0.999692667,
                    "unit" : "X"
                }
            ],
            "strain" : {
                "sbh_uri" : "https://hub.sd2e.org/user/sd2e/design/MG1655_empty_landing_pads/1",
                "label" : "MG1655_empty_landing_pads",
                "lab_id" : "name.ginkgo.346047"
            },
            "temperature" : {
                "value" : 37.0,
                "unit" : "celsius"
            },
            "replicate" : 4,
            "reference_sample_id" : "sample.ginkgo.12726577.experiment.ginkgo.19606.19637.19708.19709",
            "control_type" : "EMPTY_VECTOR",
            "derived_from" : [ ],
            "derived_using" : [ ],
            "generated_by" : [ ]
        },
        "measurement" : {
            "timepoint" : {
                "value" : 6.5,
                "unit" : "hour"
            },
            "measurement_type" : "PLATE_READER",
            "measurement_name" : "NC Titration Platereader",
            "measurement_id" : "measurement.ginkgo.1.sample.ginkgo.12757493.experiment.ginkgo.19606.19637.19708.19709",
            "measurement_group_id" : "measurement.ginkgo.10244.sample.ginkgo.12757493.experiment.ginkgo.19606.19637.19708.19709"
        },
        "file" : {
            "name" : "/uploads/attachments/biotek_multi_csv/e10244/c224255.txt",
            "type" : "PLAIN",
            "lab_label" : [
                "RAW"
            ],
            "file_id" : "file.ginkgo.1.measurement.ginkgo.1.sample.ginkgo.12731291.experiment.ginkgo.19606.19637.19708.19709",
            "level" : "0",
            "derived_from" : [ ],
            "derived_using" : [ ],
            "generated_by" : [ ]
        }
    }

    assert science_view_result == science_view_expected

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
