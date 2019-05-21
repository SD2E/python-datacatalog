#!/usr/bin/python
import json
import sys
import os
import six
import collections
import pymongo
import datacatalog
import pandas

from jsonschema import validate, ValidationError
from sbol import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id, safen_filename

def convert_caltech(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # default values for FCS support; replace with trace information as available
    # TODO update
    DEFAULT_BEAD_MODEL = "SpheroTech URCP-38-2K"
    DEFAULT_BEAD_BATCH = "AJ02"
    
    # TODO update
    CALTECH_CYTOMETER_CHANNELS = ["SSC - Area", "FSC - Area", "YFP - Area"]
    CALTECH_CYTOMETER_CONFIGURATION = "agave://data-sd2e-community/ginkgo/instruments/SA3800-20180912.json"

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    # TODO sheet name may change?
    caltech_df = pandas.read_excel(input_file, sheet_name='IDs') 

    output_doc = {}

    lab = SampleConstants.LAB_CALTECH

    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []

    # We don't navtively know which experiment contains which columns - they can all be different
    # One idea: build up a map that relates column names to mapping functions
    flow_1 = "20181009-top-4-A-B-cell-variants-A-B-sampling-exp-1"
    
    # columns for exp
    exp_columns = {}
    exp_columns[flow_1] = ["well", "a", "b", "ba ratio", "atc", "iptg"]

    # column functions
    exp_column_functions = {}
    exp_column_functions[flow_1] = [SampleConstants.SAMPLE_ID, SampleConstants.STRAIN_CONCENTRATION, SampleConstants.STRAIN_CONCENTRATION, None, SampleConstants.REAGENT_CONCENTRATION, SampleConstants.REAGENT_CONCENTRATION]

    # exp measurement type
    exp_mt = {}
    exp_mt[flow_1] = SampleConstants.MT_FLOW

    # exp measurement key
    exp_mk = {}
    exp_mk[flow_1] = "flow 1"

    # exp relative path to files
    exp_rel_path = {}
    exp_rel_path[flow_1] = "0"

    matched_exp_key = None
    matched_exp_cols = None
    matched_exp_functions = None
    header_row_values = list(caltech_df.columns.values)
    for exp_key in exp_columns:
        exp_col_list = exp_columns[exp_key]
        match_header = all([header in header_row_values for header in exp_col_list])
        if match_header:
            matched_exp_key = exp_key
            matched_exp_cols = exp_col_list
            matched_exp_functions = exp_column_functions[exp_key]
            break
    if matched_exp_key == None:
        raise ValueError("Could not match caltech experiment headers {}".format(input_file))

    # use the matched_exp_key as the reference
    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = matched_exp_key
    map_experiment_reference(config, output_doc)

    # use matching exp key, e.g. 20181009-top-4-A-B-cell-variants-A--B-sampling-exp-1
    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(matched_exp_key, lab)

    measurement_key = exp_mk[matched_exp_key]

    replicate_count = {}

    for caltech_index, caltech_sample in caltech_df.iterrows():

        sample_doc = {}
        contents = []
        well_id = None

        value_string = ""

        for index, column_name in enumerate(matched_exp_cols):
            value = caltech_sample[column_name]
            function = matched_exp_functions[index]

            if function == SampleConstants.SAMPLE_ID:
                sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(value, lab, output_doc)
                well_id = value
            elif function == SampleConstants.STRAIN_CONCENTRATION:
                # add as reagent with concentration value
                # TODO: concentration units?
                contents.append(create_media_component(output_doc.get(SampleConstants.EXPERIMENT_ID), column_name, column_name, lab, sbh_query, value))
                # build up a string of values that define this sample
                value_string = value_string + str(value)
            elif function == SampleConstants.REAGENT_CONCENTRATION:
                # TODO: concentration units?
                contents.append(create_media_component(output_doc.get(SampleConstants.EXPERIMENT_ID), column_name, column_name, lab, sbh_query, value))
                value_string = value_string + str(value)
            elif function == None:
                # skip
                continue
            else:
                raise ValueError("Unknown function {}".format(function))

        # have we seen this value before?
        if not value_string in replicate_count:
            replicate_count[value_string] = 0
            sample_doc[SampleConstants.REPLICATE] = 0
        else:
            replicate = replicate_count[value_string]
            replicate = replicate + 1
            replicate_count[value_string] = replicate

            sample_doc[SampleConstants.REPLICATE] = replicate

        if len(contents) > 0:
            sample_doc[SampleConstants.CONTENTS] = contents

        # TODO: temperature
        # TODO: timepoint   

        measurement_doc = {}
        measurement_doc[SampleConstants.FILES] = []
        measurement_doc[SampleConstants.MEASUREMENT_TYPE] = exp_mt[matched_exp_key]
        measurement_doc[SampleConstants.MEASUREMENT_NAME] = matched_exp_key + " flow cytometry"

        # generate a measurement id unique to this sample
        measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(str(1), output_doc[SampleConstants.LAB], sample_doc, output_doc)

        # record a measurement grouping id to find other linked samples and files
        measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(measurement_key, output_doc[SampleConstants.LAB], sample_doc, output_doc)

        relative_path = ""
        if matched_exp_key in exp_rel_path:
            relative_path = exp_rel_path[matched_exp_key]

        # sample id -> well name -> filename.csv?
        # TODO this may not hold
        filename = os.path.join(relative_path, well_id + ".csv")
        file_id = namespace_file_id(str(1), output_doc[SampleConstants.LAB], measurement_doc, output_doc)
        file_type = SampleConstants.infer_file_type(filename)
        measurement_doc[SampleConstants.FILES].append(
            {SampleConstants.M_NAME: filename,
             SampleConstants.M_TYPE: file_type,
             SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
             SampleConstants.FILE_ID: file_id,
             SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})
      

        if SampleConstants.MEASUREMENTS not in sample_doc:
            sample_doc[SampleConstants.MEASUREMENTS] = []
        sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)
        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    try:
        validate(output_doc, schema)

        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join(
                    "output/caltech", os.path.basename(input_file))
            else:
                path = output_file

            if path.endswith(".xlsx"):
                path = path[:-5] + ".json"

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
            if file_path.endswith(".xlsx"):
                convert_caltech(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_caltech(sys.argv[1], sys.argv[2])
