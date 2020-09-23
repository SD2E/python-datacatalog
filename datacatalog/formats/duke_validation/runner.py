#!/usr/bin/python
import json
import sys
import os
import six
import collections
import pymongo
import datacatalog
import pandas
import xlrd
import math

import datetime
from jsonschema import validate, ValidationError
from sbol2 import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_field_id, namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id, safen_filename

def convert_duke_validation(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    try:
        duke_validation_df = pandas.read_excel(input_file, sheet_name='Lib QC')
    except xlrd.biffh.XLRDError:
        read_first = pandas.read_excel(input_file)
        duke_validation_df = read_first
    
    output_doc = {}

    lab = SampleConstants.LAB_DUKE_HAASE

    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []

    index_adjustment = 0 
    is_labeled = False

    # Hasse validation specific RNASeq metadata
    VIRAL_LOAD = "Viral Load (RNA cp/ml)"
    LABEL_TRUTH = "label_truth"

    EXPERIMENT_REFERENCE = "experiment_reference"
    experiment_reference = None
    EXPERIMENT_ID = "experiment_id"
    eid = None

    validation_keys = [LABEL_TRUTH, VIRAL_LOAD, "sample_group", "Well # for CovidSeq Prep", "RNA/DNA (ul)", "H2O", "Index", "Lib Qubit (ng/ul)", "Lib Size", "Molarity", "Dilute for TapeStation", "4 nM dilution", "EB", "Qubit of diluted lib (ng/ul)", "Actual nM", "Volume to Pool"]

    for duke_validation_index, duke_validation_sample in duke_validation_df.iterrows():

        if experiment_reference == None and EXPERIMENT_REFERENCE in duke_validation_sample:
            experiment_reference = duke_validation_sample[EXPERIMENT_REFERENCE]

        if eid == None and EXPERIMENT_ID in duke_validation_sample:
            eid = duke_validation_sample[EXPERIMENT_ID]

        if VIRAL_LOAD in duke_validation_sample:
            viral_load_value = duke_validation_sample[VIRAL_LOAD]
            if viral_load_value > 20:
                is_labeled = True
                break

    if is_labeled:
        validation_metadata_key = "labeled_haase_validation_rnaseq_metadata"
    else:
        validation_metadata_key = "haase_validation_rnaseq_metadata"


    for duke_validation_index, duke_validation_sample in duke_validation_df.iterrows():

        if SampleConstants.EXPERIMENT_REFERENCE not in output_doc:

            output_doc[SampleConstants.EXPERIMENT_REFERENCE] = experiment_reference
            map_experiment_reference(config, output_doc)

            output_doc[SampleConstants.EXPERIMENT_ID] = eid

        sample_doc = {}

        well_label = None
        sample_well = None
        if "Well" in duke_validation_sample and "sample_id" in duke_validation_sample:
            sample_well = duke_validation_sample["sample_id"]
            well_label = duke_validation_sample["Well"]
            sample_well_bak = sample_well
        else:
            sample_well = duke_validation_sample["customer label"]
            if isinstance(sample_well, str):
                try:
                    float_check = float(sample_well)
                    sample_well = duke_validation_sample["Sample Name"]
                except ValueError:
                    pass
            elif isinstance(sample_well, float):
                sample_well = duke_validation_sample["Sample Name"]

            sample_well_bak = sample_well

            if isinstance(sample_well, float) and math.isnan(sample_well):
                continue

        # clean up spaces in sample names
        if " " in sample_well:
            sample_well = sample_well.replace(" ", "_")

        # clean up spaces in filenames
        if " " in sample_well_bak:
            sample_well_bak = sample_well_bak.replace(" ", "-")

        if "Index" in duke_validation_sample:
            lib_size = duke_validation_sample["Index"]
            if isinstance(lib_size, float) and math.isnan(lib_size):
                # skip and decrement counter
                index_adjustment = index_adjustment - 1
                continue

        #print(sample_well)
        #print(duke_validation_sample)
        replicate = 1
        if isinstance(sample_well, str) and "-" in sample_well:
            well_split = sample_well.split("-")
            try:
                sample_well = sample_well.replace("-","_")
                replicate = int(well_split[-1])
            except ValueError:
                # e.g. DHVI-PosA
                pass

        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(sample_well, lab, output_doc)
        sample_doc[SampleConstants.REPLICATE] = replicate
   
        if well_label is not None:
            sample_doc[SampleConstants.WELL_LABEL] = well_label

        measurement_doc = {}
        measurement_doc[SampleConstants.FILES] = []
        measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_RNA_SEQ
        measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(1, lab, sample_doc, output_doc)
        measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(SampleConstants.MT_RNA_SEQ + "_1", lab, sample_doc, output_doc)

        validation_metadata = {}
        for validation_key in validation_keys:
            try:
                validation_value = duke_validation_sample[validation_key]
                if validation_key in [LABEL_TRUTH,VIRAL_LOAD] and isinstance(validation_value, float) and math.isnan(validation_value):
                    continue
                validation_metadata[validation_key] = validation_value
            except KeyError:
                pass

        measurement_doc[validation_metadata_key] = validation_metadata

        file_id = namespace_file_id(1, lab, measurement_doc, output_doc)

        #FASTQ files are named with the sample name and the sample number, 
        # which is a numeric assignment based on the order in the sample sheet that a 
        # sample ID first appeared in a given lane. Example:
        #<SampleName>_S1_L001_R1_001.fastq.gz\
        #A1_S1_R1_001.fastq.gz
        filename = sample_well_bak + "_S" + str((int(duke_validation_index) + 1 + index_adjustment)) + "_R1_001.fastq.gz"

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
                    "output/duke_haase", os.path.basename(input_file))
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
                convert_duke_haase(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_duke_validation(sys.argv[1], sys.argv[2])
