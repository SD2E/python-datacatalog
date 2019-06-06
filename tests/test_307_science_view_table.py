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
            "value" : 37,
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
                "value" : 37,
                "unit" : "celsius"
            },
            "replicate" : 4,
            "reference_sample_id" : "sample.ginkgo.12726577.experiment.ginkgo.19606.19637.19708.19709",
            "control_type" : "EMPTY_VECTOR"
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

