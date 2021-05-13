#!/usr/bin/python
import json
import sys
import os
import six
import pymongo
import datacatalog
import re

from datacatalog import mongo

from jsonschema import validate, ValidationError
from sbol2 import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id, safen_filename


"""
Schema closely aligns with V1 target schema
Walk and expand to dictionary/attribute blocks
as necessary
"""
def convert_tulane(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    tulane_doc = json.load(open(input_file, encoding=encoding))

    output_doc = {}
    lab = SampleConstants.LAB_TULANE

    original_experiment_id = tulane_doc[SampleConstants.EXPERIMENT_ID]
    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(original_experiment_id, lab)

    output_doc[SampleConstants.CHALLENGE_PROBLEM] = tulane_doc[SampleConstants.CHALLENGE_PROBLEM]
    output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = tulane_doc[SampleConstants.EXPERIMENT_REFERENCE]

    map_experiment_reference(config, output_doc)

    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []
    samples_w_data = 0
    if SampleConstants.CYTOMETER_CONFIG in tulane_doc:
        output_doc[SampleConstants.CYTOMETER_CONFIG] = tulane_doc[SampleConstants.CYTOMETER_CONFIG]
        cytometer_channels = []
        for channel in output_doc[SampleConstants.CYTOMETER_CONFIG]['channels']:
          cytometer_channels.append(channel['name'])


    for tulane_sample in tulane_doc["tulane_samples"]:
        sample_doc = {}

        sample_id = tulane_sample["sample_id"]
        
        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(sample_id, lab, output_doc)
        sample_doc[SampleConstants.LAB_SAMPLE_ID] = namespace_sample_id(sample_id, lab, None)

        if SampleConstants.STRAIN in tulane_sample:
            strain = tulane_sample[SampleConstants.STRAIN]
            sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, "MediaControl", "MediaControl", lab, sbh_query, strain=False)
            
        if SampleConstants.CONTROL_TYPE in tulane_sample:
            sample_doc[SampleConstants.CONTROL_TYPE] = tulane_sample[SampleConstants.CONTROL_TYPE]

        if SampleConstants.CONTROL_CHANNEL in tulane_sample:
            sample_doc[SampleConstants.CONTROL_CHANNEL] = tulane_sample[SampleConstants.CONTROL_CHANNEL]

        measurement_counter = 1

        for file in tulane_sample[SampleConstants.FILES]:
            measurement_doc = {}

            measurement_doc[SampleConstants.FILES] = []

            measurement_type = file[SampleConstants.M_TYPE]

            file_name = file[SampleConstants.M_NAME]
            # same logic as uploads manager
            file_name = safen_filename(file_name)

            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type

            # append the type so we have a distinct id per actual grouped measurement
            typed_measurement_id = '.'.join([str(measurement_counter), measurement_type])

            # generate a measurement id unique to this sample
            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(str(measurement_counter), output_doc[SampleConstants.LAB], sample_doc, output_doc)

            # record a measurement grouping id to find other linked samples and files
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(typed_measurement_id, output_doc[SampleConstants.LAB], sample_doc, output_doc)

            file_type = SampleConstants.infer_file_type(file_name)
            file_name_final = file_name

            if file_name_final.startswith("/"):
                file_name_final = file_name_final[1:]

            measurement_doc[SampleConstants.FILES].append(
                {SampleConstants.M_NAME: file_name_final,
                 SampleConstants.M_TYPE: file_type,
                 SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
                 # measurements and files here are 1:1
                 SampleConstants.FILE_ID: namespace_file_id("1", output_doc[SampleConstants.LAB], measurement_doc, output_doc),
                 SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})

            if SampleConstants.MEASUREMENTS not in sample_doc:
                sample_doc[SampleConstants.MEASUREMENTS] = []
            sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)
            samples_w_data = samples_w_data + 1
            #print('sample {} / measurement {} contains {} files'.format(sample_doc[SampleConstants.SAMPLE_ID], file_name, len(measurement_doc[SampleConstants.FILES])))

            measurement_counter = measurement_counter + 1

        if SampleConstants.MEASUREMENTS not in sample_doc:
            sample_doc[SampleConstants.MEASUREMENTS] = []
        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    print('Samples in file: {}'.format(len(tulane_doc)))
    print('Samples with data: {}'.format(samples_w_data))

    try:
        validate(output_doc, schema)
        # if verbose:
        # print(json.dumps(output_doc, indent=4))
        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join(
                    "output/tulane", os.path.basename(input_file))
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

if __name__ == "__main__":
    path = sys.argv[2]
    if os.path.isdir(path):
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            print(file_path)
            if file_path.endswith(".js") or file_path.endswith(".json"):
                convert_tulane(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_tulane(sys.argv[1], sys.argv[2])
