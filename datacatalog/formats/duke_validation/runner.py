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
from sbol import *
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

    # Hasse validation specific RNASeq metadata
    validation_keys = ["Viral Load (RNA cp/mL)", "Well # for CovidSeq Prep", "RNA/DNA (ul)", "H2O", "Index", "Lib Qubit (ng/ul)", "Lib Size", "Molarity", "Dilute for TapeStation", "4 nM dilution", "EB", "Qubit of diluted lib (ng/ul)", "Actual nM", "Volume to Pool"]

    for duke_validation_index, duke_validation_sample in duke_validation_df.iterrows():

        # TODO add reference/url, challenge problem, and EID to Duke Validation trace
        if SampleConstants.EXPERIMENT_REFERENCE not in output_doc:
            #output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = "https://docs.google.com/document/d/1XQ4Rt8oz-jS8otL6EC_iRHdKexMtIzx5YaUwn5_41vg"
            output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = "https://docs.google.com/document/d/1Gck0rftZSsuk_se6HM4T09Pi0Cxyt80BA3YtrDrB0do"
            map_experiment_reference(config, output_doc)

            #output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id("DHVI-Panel_QC_Library_Dilution_Pooling_COVID-Seq-TEST", lab)
            output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id("6406_QC_Library_Dilution_Pooling_LLR", lab)
            experiment_id = output_doc.get(SampleConstants.EXPERIMENT_ID)

        sample_doc = {}
   
        sample_well = duke_validation_sample["Sample Name"]
        if isinstance(sample_well, float) and math.isnan(sample_well):
            continue

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
                replicate = int(well_split[-1])
            except ValueError:
                # e.g. DHVI-PosA
                pass

        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(sample_well, lab, output_doc)
        sample_doc[SampleConstants.REPLICATE] = replicate
   
        measurement_doc = {}
        measurement_doc[SampleConstants.FILES] = []
        measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_RNA_SEQ
        measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(1, lab, sample_doc, output_doc)
        measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(SampleConstants.MT_RNA_SEQ + "_1", lab, sample_doc, output_doc)

        validation_metadata = {}
        for validation_key in validation_keys:
            try:
                validation_value = duke_validation_sample[validation_key]
                validation_metadata[validation_key] = validation_value
            except KeyError:
                pass
        measurement_doc["haase_validation_rnaseq_metadata"] = validation_metadata

        file_id = namespace_file_id(1, lab, measurement_doc, output_doc)

        #FASTQ files are named with the sample name and the sample number, 
        # which is a numeric assignment based on the order in the sample sheet that a 
        # sample ID first appeared in a given lane. Example:
        #<SampleName>_S1_L001_R1_001.fastq.gz\
        #A1_S1_R1_001.fastq.gz
        filename = sample_well + "_S" + str((int(duke_validation_index) + 1 + index_adjustment)) + "_R1_001.fastq.gz"

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
