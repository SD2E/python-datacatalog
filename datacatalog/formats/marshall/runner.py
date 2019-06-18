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

def convert_marshall(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    # TODO sheet name may change?
    marshall_df = pandas.read_excel(input_file, sheet_name='TACC_genomics_metadata')

    output_doc = {}

    lab = SampleConstants.LAB_MARSHALL

    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []

    # We don't navtively know which experiment contains which columns - they can all be different
    # Build up a map that relates column names to mapping functions

    # columns for exp
    exp_columns = {}
    # column functions
    exp_column_functions = {}
    # exp measurement type
    exp_mt = {}
    # exp measurement key
    exp_mk = {}
    #exp file_columns
    exp_r1_r2 = {}

    sg_rna_seq = "TACC-genomics-metadata"
    exp_columns[sg_rna_seq] = ["sample ID", "pedigree_ID", "generation", "stage", "sex", "species", \
                               "geographic_origin", "NGS_protocol", "Sequencing Platform", \
                               "Sequencing chemistry", "file_type", "file_name_r1", "file_name_r2"]

    # TODO map other metadata
    exp_column_functions[sg_rna_seq] = [SampleConstants.SAMPLE_ID, None, None, None, None, SampleConstants.STRAIN, \
                                        None, None, None, None, None, None, None]
    exp_mt[sg_rna_seq] = [SampleConstants.MT_RNA_SEQ]
    exp_mk[sg_rna_seq] = ["TACC-genomics-metadata RNASeq"]
    exp_r1_r2[sg_rna_seq] = ["file_name_r1", "file_name_r2"]

    matched_exp_key = None
    matched_exp_cols = None
    matched_exp_functions = None
    header_row_values = list(marshall_df.columns.values)
    for exp_key in exp_columns:
        exp_col_list = exp_columns[exp_key]
        match_header = all([header in header_row_values for header in exp_col_list])
        if match_header:
            matched_exp_key = exp_key
            matched_exp_cols = exp_col_list
            matched_exp_functions = exp_column_functions[exp_key]
            break
    if matched_exp_key == None:
        raise ValueError("Could not match Marshall experiment headers {}".format(input_file))

    # use the matched_exp_key as the reference
    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = matched_exp_key

    # TODO: Update reference to Google drive
    # Currently using SafeGenes/TACC-genomics-metadata stub
    map_experiment_reference(config, output_doc)

    # use matching exp key, e.g. TACC-genomics-metadata
    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(matched_exp_key, lab)

    replicate_count = {}

    for marshall_index, marshall_sample in marshall_df.iterrows():

        sample_doc = {}
        contents = []
        sample_id = None

        value_string = ""

        for index, column_name in enumerate(matched_exp_cols):
            value = marshall_sample[column_name]
            function = matched_exp_functions[index]

            # build up a string of values that define this sample
            value_string = value_string + str(value)

            if function == SampleConstants.SAMPLE_ID:
                sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(value, lab, output_doc)
                sample_id = value
            elif function == SampleConstants.STRAIN:
                 sample_doc[SampleConstants.STRAIN] = create_mapped_name(output_doc.get(SampleConstants.EXPERIMENT_ID), value, value, lab, sbh_query, strain=True)
            elif function == SampleConstants.REAGENT_CONCENTRATION:
                contents.append(create_media_component(output_doc.get(SampleConstants.EXPERIMENT_ID), column_name, column_name, lab, sbh_query, value))
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

        measurement_key  = exp_mk[matched_exp_key]

        for measurement_key_index, measurement_key_value in enumerate(measurement_key):
            measurement_doc = {}
            measurement_doc[SampleConstants.FILES] = []
            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = exp_mt[matched_exp_key][measurement_key_index]
            measurement_doc[SampleConstants.MEASUREMENT_NAME] = measurement_key_value

            # generate a measurement id unique to this sample
            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(str(measurement_key_index + 1), output_doc[SampleConstants.LAB], sample_doc, output_doc)

            # record a measurement grouping id to find other linked samples and files
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(measurement_key_value, output_doc[SampleConstants.LAB], sample_doc, output_doc)

            for fn_index, fn_column in enumerate(exp_r1_r2[matched_exp_key]):
                filename = marshall_sample[fn_column]
                file_id = namespace_file_id(str(fn_index + 1), output_doc[SampleConstants.LAB], measurement_doc, output_doc)
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
                    "output/marshall", os.path.basename(input_file))
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
                convert_marshall(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_marshall(sys.argv[1], sys.argv[2])
