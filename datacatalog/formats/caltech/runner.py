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
from sbol2 import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id, safen_filename

# create a named flow control sample (positive or negative)
def create_flow_control_sample(filename, measurement_name, channels, cytometer_configuration, output_doc, negative_control, positive_control, positive_control_channel):
    sample_doc = {}
    sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id("sample_" + filename, output_doc[SampleConstants.LAB], output_doc)
    sample_doc[SampleConstants.REPLICATE] = 0

    if negative_control:
        sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
    elif positive_control:
        sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
        sample_doc[SampleConstants.CONTROL_CHANNEL] = positive_control_channel

    measurement_doc = {}
    measurement_doc[SampleConstants.FILES] = []
    measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_FLOW
    measurement_doc[SampleConstants.MEASUREMENT_NAME] = measurement_name
    measurement_doc[SampleConstants.M_CHANNELS] = channels
    measurement_doc[SampleConstants.M_INSTRUMENT_CONFIGURATION] = cytometer_configuration
    measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(str(1), output_doc[SampleConstants.LAB], sample_doc, output_doc)
    measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(measurement_name, output_doc[SampleConstants.LAB], sample_doc, output_doc)

    file_id = namespace_file_id(str(1), output_doc[SampleConstants.LAB], measurement_doc, output_doc)
    file_type = SampleConstants.infer_file_type(filename)
    measurement_doc[SampleConstants.FILES].append(
        {SampleConstants.M_NAME: filename,
         SampleConstants.M_TYPE: file_type,
         SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
         SampleConstants.FILE_ID: file_id,
         SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})


    sample_doc[SampleConstants.MEASUREMENTS] = []
    sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)

    output_doc[SampleConstants.SAMPLES].append(sample_doc)

def convert_caltech(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

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
    # Idea: build up a map that relates column names to mapping functions
    
    # columns for exp
    exp_columns = {}
    # column functions
    exp_column_functions = {}
    # exp measurement type
    exp_mt = {}
    # exp measurement key
    exp_mk = {}
    # exp relative path to files
    exp_rel_path = {}
    # exp column units
    exp_column_units = {}
    # time
    exp_time = {}
    # temp
    exp_temp = {}
    # flow cytometer channels, configuration and controls
    exp_cytometer_channels = {}
    exp_cytometer_configuration = {}
    exp_negative_controls = {}
    exp_positive_controls = {}

    flow_1 = "20181009-top-4-A-B-cell-variants-A-B-sampling-exp-1"
    exp_columns[flow_1] = ["well", "a", "b", "ba ratio", "atc", "iptg"]
    exp_column_functions[flow_1] = [SampleConstants.SAMPLE_ID, SampleConstants.STRAIN_CONCENTRATION, SampleConstants.STRAIN_CONCENTRATION, None, SampleConstants.REAGENT_CONCENTRATION, SampleConstants.REAGENT_CONCENTRATION]
    exp_mt[flow_1] = [SampleConstants.MT_FLOW]
    exp_mk[flow_1] = ["0_flow"]
    exp_rel_path[flow_1] = ["0"]
    exp_time[flow_1] = ["0:hour"]
    exp_temp[flow_1] = ["37:celsius"]

    exp_cytometer_channels[flow_1] = ["FSC-A", "SSC-A", "CFP/VioBlue-A", "GFP/FITC-A"]
    exp_cytometer_configuration[flow_1] = "agave://data-sd2e-projects.sd2e-project-21/ReedM-index/A_eq_B/20190214_A_eq_B_mar_1/20190214-A-B-mar-1-cc.json"
    exp_negative_controls[flow_1] = ["0/blank-RDM2019-02-14.0001.fcs"]
    exp_positive_controls[flow_1] = {}
    exp_positive_controls[flow_1]["CFP/VioBlue-A"] = ["0/bfp-RDM2019-02-14.0001.fcs"]
    exp_positive_controls[flow_1]["GFP/FITC-A"] = ["0/yfp-RDM2019-02-14.0002.fcs"]

    flow_2 = "20190214-A-B-mar-1"
    exp_columns[flow_2] = ["well", "iptg", "sal", "a", "b"]
    exp_column_functions[flow_2] = [SampleConstants.SAMPLE_ID, SampleConstants.REAGENT_CONCENTRATION, SampleConstants.REAGENT_CONCENTRATION, SampleConstants.STRAIN_CONCENTRATION, SampleConstants.STRAIN_CONCENTRATION]
    exp_mt[flow_2] = [SampleConstants.MT_FLOW, SampleConstants.MT_FLOW]
    exp_mk[flow_2] = ["0_flow", "18_flow"]
    exp_rel_path[flow_2] = ["0_flow", "18_flow"]
    exp_column_units[flow_2] = [None, "micromole", "micromole", None, None]
    exp_time[flow_2] = ["0:hour", "18:hour"]
    exp_temp[flow_2] = ["37:celsius", "37:celsius"]

    exp_cytometer_channels[flow_2] = ["FSC-A", "SSC-A", "CFP/VioBlue-A", "GFP/FITC-A"]
    exp_cytometer_configuration[flow_2] = "agave://data-sd2e-projects.sd2e-project-21/ReedM-index/A_eq_B/20190214_A_eq_B_mar_1/20190214-A-B-mar-1-cc.json"
    exp_negative_controls[flow_2] = ["0_flow/blank-RDM2019-02-14.0001.fcs"]
    exp_positive_controls[flow_2] = {}
    exp_positive_controls[flow_2]["CFP/VioBlue-A"] = ["0_flow/A5.csv"]
    exp_positive_controls[flow_2]["GFP/FITC-A"] = ["0_flow/yfp-RDM2019-02-14.0002.fcs"]

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

    replicate_count = {}

    for caltech_index, caltech_sample in caltech_df.iterrows():

        measurement_key  = exp_mk[matched_exp_key]

        for measurement_key_index, measurement_key_value in enumerate(measurement_key):

            # skip if this is a control
            skip = False

            sample_doc = {}
            contents = []
            well_id = None

            value_string = ""

            for index, column_name in enumerate(matched_exp_cols):
                value = caltech_sample[column_name]
                function = matched_exp_functions[index]

                if function == SampleConstants.SAMPLE_ID:
                    # 1:1 sample measurements
                    sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(value + "_" + str(measurement_key_index), lab, output_doc)
                    well_id = value
                elif function == SampleConstants.STRAIN_CONCENTRATION:
                    # add as reagent with concentration value
                    # 'x' = not present/0
                    if value == 'x':
                        value = 0

                    contents.append(create_media_component(output_doc.get(SampleConstants.EXPERIMENT_ID), column_name, column_name, lab, sbh_query, value))
                    # build up a string of values that define this sample
                    value_string = value_string + str(value)
                elif function == SampleConstants.REAGENT_CONCENTRATION:
                    if matched_exp_key in exp_column_units:
                        unit = exp_column_units[matched_exp_key][index]
                        value_unit = str(value) + ":" + str(unit)
                        contents.append(create_media_component(output_doc.get(SampleConstants.EXPERIMENT_ID), column_name, column_name, lab, sbh_query, value_unit))
                    else:
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

            measurement_doc = {}
            measurement_doc[SampleConstants.FILES] = []
            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = exp_mt[matched_exp_key][measurement_key_index]
            measurement_doc[SampleConstants.MEASUREMENT_NAME] = measurement_key_value

            # Fill in Flow information, if known
            if measurement_doc[SampleConstants.MEASUREMENT_TYPE] == SampleConstants.MT_FLOW:
                if matched_exp_key in exp_cytometer_channels:
                    measurement_doc[SampleConstants.M_CHANNELS] = exp_cytometer_channels[matched_exp_key]
                if matched_exp_key in exp_cytometer_configuration:
                    measurement_doc[SampleConstants.M_INSTRUMENT_CONFIGURATION] = exp_cytometer_configuration[matched_exp_key]

            if matched_exp_key in exp_time:
                time = exp_time[matched_exp_key][measurement_key_index]
                measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time)

            if SampleConstants.TEMPERATURE not in sample_doc:
                if matched_exp_key in exp_temp:
                    temp = exp_temp[matched_exp_key][measurement_key_index]
                    sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(temp)

            # generate a measurement id unique to this sample
            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(str(measurement_key_index + 1), output_doc[SampleConstants.LAB], sample_doc, output_doc)

            # record a measurement grouping id to find other linked samples and files
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(measurement_key_value, output_doc[SampleConstants.LAB], sample_doc, output_doc)

            # sample id -> well name -> filename.csv?
            # TODO this may not hold
            fn_well = well_id + ".csv"

            if matched_exp_key in exp_negative_controls:
                for negative_control in exp_negative_controls[matched_exp_key]:
                    if negative_control.endswith(fn_well):
                        skip = True

            if matched_exp_key in exp_positive_controls:
                for positive_control_channel in exp_positive_controls[matched_exp_key]:
                    for positive_control in exp_positive_controls[matched_exp_key][positive_control_channel]:
                        if positive_control.endswith(fn_well):
                            skip = True
            if skip:
                continue

            filename = os.path.join(exp_rel_path[matched_exp_key][measurement_key_index], fn_well)
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

    # Add flow controls, if known
    if matched_exp_key in exp_negative_controls:
        for negative_control in exp_negative_controls[matched_exp_key]:
            create_flow_control_sample(negative_control, "negative flow control", \
                exp_cytometer_channels[matched_exp_key], exp_cytometer_configuration[matched_exp_key], output_doc, \
                    True, False, None)

    if matched_exp_key in exp_positive_controls:
        for positive_control_channel in exp_positive_controls[matched_exp_key]:
            for positive_control in exp_positive_controls[matched_exp_key][positive_control_channel]:
                create_flow_control_sample(positive_control, "positive flow control", \
                    exp_cytometer_channels[matched_exp_key], exp_cytometer_configuration[matched_exp_key], output_doc, \
                        False, True, positive_control_channel)

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
