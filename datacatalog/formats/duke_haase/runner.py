#!/usr/bin/python
import json
import sys
import os
import six
import collections
import pymongo
import datacatalog

from jsonschema import validate, ValidationError
from sbol import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_field_id, namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id, safen_filename

def convert_duke_haase(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    input_fp_csvreader = csv.reader(open(input_file))
    
    output_doc = {}

    lab = SampleConstants.LAB_DUKE_HAASE

    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []

    # TODO - Duke adds this to lab trace
    output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = "https://docs.google.com/document/d/1D9hXd5Hmeb75FGH0sGq93KjCOjHKD26x8HXluNJLII8"
    map_experiment_reference(config, output_doc)

    # TODO Duke adds this to lab trace
    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(os.path.basename(input_file).split(".")[0], lab)

    experiment_id = output_doc.get(SampleConstants.EXPERIMENT_ID)

    sample_counter = 1
    for row in input_fp_csvreader:
        if row[0] == "Strain":
            continue
        else:

            sample_doc = {}
            contents = []
            strain = row[0]
            replicate = row[1]
            treatment = row[2]

            # TODO - Duke provides unique aliquot
            sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(sample_counter, lab, output_doc)

            sample_doc[SampleConstants.STRAIN] = create_mapped_name(experiment_id, strain, strain, lab, sbh_query, strain=True)

            sample_doc[SampleConstants.REPLICATE] = int(replicate)

            # Controls are specified in the trace
            # TODO Rob add positive/negative
            if treatment == "Control":
                if strain != "NOR 00":
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
                else:
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
            else:

                treatment_concentration = row[3]
                treatment_concentration_unit = row[4]
                treatment_time = row[5]
                treatment_time_unit = row[6]

                contents_append_value = create_media_component(experiment_id, treatment, treatment, lab, sbh_query, treatment_concentration + ":" + treatment_concentration_unit)
                contents_append_value[SampleConstants.TIMEPOINT] = { SampleConstants.VALUE : int(treatment_time), SampleConstants.UNIT : treatment_time_unit }

                contents.append(contents_append_value)

            if len(contents) > 0:
                sample_doc[SampleConstants.CONTENTS] = contents

            # TODO populate additional sample data from CSV
            # Samples schema cannot currently support
            CFU = row[7]
            culture_cells_ml = row[8]
            estimated_cells_plated = row[9]
            estimated_cells_ml = row[10]
            percent_killed = row[11]
            date_of_experiment = row[12]

            measurement_doc = {}
            measurement_doc[SampleConstants.FILES] = []
            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_CFU

            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(1, lab, sample_doc, output_doc)
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(SampleConstants.MT_CFU + "_1", lab, sample_doc, output_doc)

            file_id = namespace_file_id(1, lab, measurement_doc, output_doc)
            file_type = SampleConstants.infer_file_type(input_file)
            measurement_doc[SampleConstants.FILES].append(
                {SampleConstants.M_NAME: input_file,
                 SampleConstants.M_TYPE: file_type,
                 SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
                 SampleConstants.FILE_ID: file_id,
                 SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})

            if SampleConstants.MEASUREMENTS not in sample_doc:
                sample_doc[SampleConstants.MEASUREMENTS] = []
            sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)

            output_doc[SampleConstants.SAMPLES].append(sample_doc)

            sample_counter = sample_counter + 1

    try:
        validate(output_doc, schema)

        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join(
                    "output/duke_haase", os.path.basename(input_file))
            else:
                path = output_file

            if path.endswith(".csv"):
                path = path[:-4] + ".json"

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
        convert_marshall(sys.argv[1], sys.argv[2])
