#!/usr/bin/python
import json
import sys
import os
import six
import re

from jsonschema import validate, ValidationError
from sbol import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ..agavehelpers import AgaveHelper
from .common import SampleConstants
from .common import namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id
from .mappings import SampleContentsFilter


attributes_attr = "attributes"
files_attr = "files"

def convert_sample_attributes(schema_file, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)

    schema = json.load(open(schema_file))
    sample_attributes_doc = json.load(open(input_file))

    output_doc = {}

    output_doc[SampleConstants.SAMPLES] = []

    lab = None

    exp_id_re = re.compile("agave:\/\/.*\/(.*)\/\d\/instrument_output")

    for sample_attributes_sample in sample_attributes_doc:
        sample_doc = {}

        # try to figure out the lab, experiment_id, cp, etc from the filename
        if lab is None and attributes_attr in sample_attributes_sample and files_attr in sample_attributes_sample[attributes_attr]:
            for file in sample_attributes_sample[attributes_attr][files_attr]:

                # lab mapping
                if "transcriptic" in file and SampleConstants.LAB not in output_doc:
                    lab = SampleConstants.LAB_TX
                    output_doc[SampleConstants.LAB] = lab

                # CP mapping
                if "yeast-gates" in file and SampleConstants.CHALLENGE_PROBLEM not in output_doc:
                    output_doc[SampleConstants.CHALLENGE_PROBLEM] = SampleConstants.CP_YEAST_GATES
                    # provide this manually
                    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = "Yeast-Gates"

                # Tricky. Parse experiment id out out of the below (r1bbktv6x4xke)
                # agave://data-sd2e-community/transcriptic/yeast-gates_q0/r1bbktv6x4xke/3/instrument_output/s877_R31509.fcs ?
                exp_match = exp_id_re.match(file)
                if exp_match and SampleConstants.EXPERIMENT_ID not in output_doc:
                    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(exp_match.group(1), lab)

                map_experiment_reference(config, output_doc)

        if lab is None:
            raise ValueError("Could not parse lab from sample {}".format(sample_attributes_sample))

        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(str(sample_attributes_sample["sample"]), lab)

        # TODO
        # Contents
        # Media, replicate, timepoint, temperature etc.
        # Measurements and files
        sample_doc[SampleConstants.MEASUREMENTS] = []

        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    try:
        validate(output_doc, schema)
        # if verbose:
        # print(json.dumps(output_doc, indent=4))
        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join(
                    "output/sample_attributes", os.path.basename(input_file))
            else:
                path = output_file
            with open(path, 'w') as outfile:
                json.dump(output_doc, outfile, indent=4)
        return True
    except ValidationError as err:
        if enforce_validation:
            if verbose:
                print("Schema Validation Error: {0}\n".format(err))
            raise ValidationError("Schema Validation Error", err)
        else:
            if verbose:
                print("Schema Validation Error: {0}\n".format(err))
            return False
        return False

if __name__ == "__main__":
    path = sys.argv[2]
    if os.path.isdir(path):
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            print(file_path)
            if file_path.endswith(".js") or file_path.endswith(".json"):
                convert_sample_attributes(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_sample_attributes(sys.argv[1], sys.argv[2])
