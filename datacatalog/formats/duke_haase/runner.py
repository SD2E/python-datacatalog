#!/usr/bin/python
import json
import sys
import os
import six
import collections
import pymongo
import datacatalog

import datetime
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

    headers = None
    is_cfu = False
    doe_format = "%Y%m%d"

    # This converter reads both CFU and FCS formatted metadata from Duke. They have different sets of fields
    # We key on the presence of a CFU column to determine which we are parsing
    # CFU Fields
    # 0 strain
    # 1 replicate
    # 2 treatment
    # 3 treatment_concentration
    # 4 treatment_concentration_unit
    # 5 treatment_time
    # 6 treatment_time_unit
    # 7 CFU
    # 8 culture_cells/ml
    # 9 date_of_experiment
    # 10 experiment_reference_url
    # 11 experiment_reference
    # 12 experiment_id
    # 13 parent_id
    # 14 estimated_cells_plated
    # 15 estimated_cells/ml
    # 16 percent_killed
    # 17 strain_class
    # 18 control_type
    # 19 sample_id
    #
    # FCS Fields
    # 0 strain
    # 1 replicate
    # 2 treatment
    # 3 treatment_concentration
    # 4 treatment_concentration_unit
    # 5 treatment_time
    # 6 treatment_time_unit
    # 7 culture_cells/ml
    # 8 date_of_experiment
    # 9 experiment_reference_url
    # 10 experiment_reference
    # 11 experiment_id
    # 12 parent_id
    # 13 strain_class
    # 14 control_type
    # 15 fcs_filename
    # 16 sytox_color
    # 17 sytox_concentration
    # 18 sytox_concentration_unit
    # 19 sample_id

    for row in input_fp_csvreader:
        if row[0] == "strain":
            headers = row
            if headers[7] == "CFU":
                is_cfu = True
            continue
        else:

            if SampleConstants.EXPERIMENT_REFERENCE not in output_doc:
                if is_cfu:
                    output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = row[10]
                    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(row[12], lab)
                else:
                    output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = row[9]
                    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(row[11], lab)

                map_experiment_reference(config, output_doc)
                experiment_id = output_doc.get(SampleConstants.EXPERIMENT_ID)

            sample_doc = {}
            contents = []
            strain = row[0]
            replicate = row[1]
            treatment = row[2]

            sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(row[19], lab, output_doc)

            if is_cfu:
                sample_doc[SampleConstants.REFERENCE_SAMPLE_ID] = namespace_sample_id(row[13], lab, output_doc)
            else:
                sample_doc[SampleConstants.REFERENCE_SAMPLE_ID] = namespace_sample_id(row[12], lab, output_doc)

            sample_doc[SampleConstants.STRAIN] = create_mapped_name(experiment_id, strain, strain, lab, sbh_query, strain=True)

            sample_doc[SampleConstants.REPLICATE] = int(replicate)

            m_time = None

            if len(treatment) > 0:

                treatment_concentration = row[3]
                treatment_concentration_unit = row[4]
                treatment_time = row[5]
                treatment_time_unit = row[6]

                if treatment == "heat":
                    if treatment_concentration_unit == "C":
                        sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(treatment_concentration+":celsius")
                        m_time = create_value_unit(treatment_time + ":" + treatment_time_unit)
                    else:
                        raise ValueError("Unknown temperature {}".format(treatment_concentration_unit))
                else:
                    contents_append_value = create_media_component(experiment_id, treatment, treatment, lab, sbh_query, treatment_concentration + ":" + treatment_concentration_unit)
                    contents_append_value[SampleConstants.TIMEPOINT] = { SampleConstants.VALUE : int(float(treatment_time)), SampleConstants.UNIT : treatment_time_unit }

                    contents.append(contents_append_value)

            # controls
            if is_cfu:
                strain_class = row[17]
                control_type = row[18]
            else:
                strain_class = row[13]
                control_type = row[14]
            #
            if strain_class == "Control" and control_type == "Negative":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR

            # Styox
            if not is_cfu:
                sytox = row[16]
                if len(sytox) > 0:
                    sytox = "sytox_" + sytox
                    contents.append(create_media_component(experiment_id, sytox, sytox, lab, sbh_query, row[17] + ":" + row[18]))

            if len(contents) > 0:
                sample_doc[SampleConstants.CONTENTS] = contents

            measurement_doc = {}
            measurement_doc[SampleConstants.FILES] = []
            if is_cfu:
                measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_CFU
            else:
                measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_FLOW

            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(1, lab, sample_doc, output_doc)
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(measurement_doc[SampleConstants.MEASUREMENT_TYPE] + "_1", lab, sample_doc, output_doc)

            if m_time is not None:
                measurement_doc[SampleConstants.TIMEPOINT] = m_time

            #CFU 305
            #culture_cells_ml 2.33E+07
            #estimated_cells_plated 583
            #estimated_cells_ml 1.22E+07
            #percent_killed 47.60%
            #date_of_experiment 6/10/20
            cfu_data = {}
            if is_cfu:
                cfu_data[headers[7]] = int(float(row[7]))
                cfu_data[headers[8]] = int(float(row[8]))
                cfu_data[headers[14]] = int(row[14])
                cfu_data[headers[15]] = int(float(row[15]))
                cfu_data[headers[16]] = float(row[16][:-1])
                cfu_data[headers[9]] = datetime.datetime.strptime(row[9], doe_format).strftime(doe_format)
            else:
                #culture_cells/ml
                #date_of_experiment
                cfu_data[headers[7]] = int(float(row[7]))
                cfu_data[headers[8]] = datetime.datetime.strptime(row[8], doe_format).strftime(doe_format)

            measurement_doc["cfu_data"] = cfu_data

            file_id = namespace_file_id(1, lab, measurement_doc, output_doc)
            if is_cfu:
                file_type = SampleConstants.infer_file_type(input_file)
                measurement_doc[SampleConstants.FILES].append(
                    {SampleConstants.M_NAME: experiment_id + "_cfu_and_meta.csv",
                     SampleConstants.M_TYPE: file_type,
                     SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
                     SampleConstants.FILE_ID: file_id,
                     SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})
            else:
                filename = row[15]
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
