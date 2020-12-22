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
from sbol2 import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_field_id, namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id, safen_filename

def convert_duke_haase(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    DEFAULT_BEAD_MODEL = "SpheroTech URCP-38-2K"
    DEFAULT_BEAD_BATCH = "AJ02"

    duke_cytometer_configuration = """{
        "channels": [{
                "emission_filter": {
                    "center": 488,
                    "type": "bandpass",
                    "width": 10
                },
                "excitation_wavelength": 488,
                "name": "FSC-A"
            },
            {
                "emission_filter": {
                    "center": 488,
                    "type": "bandpass",
                    "width": 10
                },
                "excitation_wavelength": 488,
                "name": "SSC-A"
            },
            {
                "emission_filter": {
                    "center": 530,
                    "type": "bandpass",
                    "width": 30
                },
                "excitation_wavelength": 488,
                "name": "BL1-A"
            },
            {
                "emission_filter": {
                    "center": 590,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 488,
                "name": "BL2-A"
            },
            {
                "emission_filter": {
                    "center": 695,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 488,
                "name": "BL3-A"
            },
            {
                "emission_filter": {
                    "center": 780,
                    "type": "bandpass",
                    "width": 60
                },
                "excitation_wavelength": 561,
                "name": "YL4-A"
            },
            {
                "emission_filter": {
                    "center": 695,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 561,
                "name": "YL3-A"
            },
            {
                "emission_filter": {
                    "center": 620,
                    "type": "bandpass",
                    "width": 15
                },
                "excitation_wavelength": 561,
                "name": "YL2-A"
            },
            {
                "emission_filter": {
                    "center": 585,
                    "type": "bandpass",
                    "width": 16
                },
                "excitation_wavelength": 561,
                "name": "YL1-A"
            },
            {
                "emission_filter": {
                    "center": 488,
                    "type": "bandpass",
                    "width": 10
                },
                "excitation_wavelength": 488,
                "name": "FSC-H"
            },
            {
                "emission_filter": {
                    "center": 488,
                    "type": "bandpass",
                    "width": 10
                },
                "excitation_wavelength": 488,
                "name": "SSC-H"
            },
            {
                "emission_filter": {
                    "center": 530,
                    "type": "bandpass",
                    "width": 30
                },
                "excitation_wavelength": 488,
                "name": "BL1-H"
            },
            {
                "emission_filter": {
                    "center": 590,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 488,
                "name": "BL2-H"
            },
            {
                "emission_filter": {
                    "center": 695,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 488,
                "name": "BL3-H"
            },
            {
                "emission_filter": {
                    "center": 780,
                    "type": "bandpass",
                    "width": 60
                },
                "excitation_wavelength": 561,
                "name": "YL4-H"
            },
            {
                "emission_filter": {
                    "center": 695,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 561,
                "name": "YL3-H"
            },
            {
                "emission_filter": {
                    "center": 620,
                    "type": "bandpass",
                    "width": 15
                },
                "excitation_wavelength": 561,
                "name": "YL2-H"
            },
            {
                "emission_filter": {
                    "center": 585,
                    "type": "bandpass",
                    "width": 16
                },
                "excitation_wavelength": 561,
                "name": "YL1-H"
            },
            {
                "emission_filter": {
                    "center": 488,
                    "type": "bandpass",
                    "width": 10
                },
                "excitation_wavelength": 488,
                "name": "FSC-W"
            },
            {
                "emission_filter": {
                    "center": 488,
                    "type": "bandpass",
                    "width": 10
                },
                "excitation_wavelength": 488,
                "name": "SSC-W"
            },
            {
                "emission_filter": {
                    "center": 530,
                    "type": "bandpass",
                    "width": 30
                },
                "excitation_wavelength": 488,
                "name": "BL1-W"
            },
            {
                "emission_filter": {
                    "center": 590,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 488,
                "name": "BL2-W"
            },
            {
                "emission_filter": {
                    "center": 695,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 488,
                "name": "BL3-W"
            },
            {
                "emission_filter": {
                    "center": 780,
                    "type": "bandpass",
                    "width": 60
                },
                "excitation_wavelength": 561,
                "name": "YL4-W"
            },
            {
                "emission_filter": {
                    "center": 695,
                    "type": "bandpass",
                    "width": 40
                },
                "excitation_wavelength": 561,
                "name": "YL3-W"
            },
            {
                "emission_filter": {
                    "center": 620,
                    "type": "bandpass",
                    "width": 15
                },
                "excitation_wavelength": 561,
                "name": "YL2-W"
            },
            {
                "emission_filter": {
                    "center": 585,
                    "type": "bandpass",
                    "width": 16
                },
                "excitation_wavelength": 561,
                "name": "YL1-W"
            }
        ]
    }"""

    duke_cytometer_configuration_object = json.loads(duke_cytometer_configuration)

    cytometer_channels = []
    for channel in duke_cytometer_configuration_object['channels']:
        if channel['name'].endswith("-A"):
            cytometer_channels.append(channel['name'])

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

    header_map = {}

    for row in input_fp_csvreader:
        if row[0] == "strain":
            headers = row

            for header_index, header in enumerate(headers):
                header_map[header] = header_index

            if "CFU" in header_map:
                is_cfu = True
            continue
        else:

            # Lookup experiment id, separate by measurement type
            if SampleConstants.EXPERIMENT_REFERENCE not in output_doc:

                if is_cfu:
                    mt = SampleConstants.MT_CFU
                else:
                    mt = SampleConstants.MT_FLOW

                output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = row[header_map["experiment_reference_url"]]

                # without measurement type - for filenames
                experiment_id_bak = row[header_map["experiment_id"]]
                output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(experiment_id_bak+"_"+mt, lab)

                map_experiment_reference(config, output_doc)
                experiment_id = output_doc.get(SampleConstants.EXPERIMENT_ID)

            sample_doc = {}
            contents = []
            strain = row[header_map["strain"]]
            replicate = row[header_map["replicate"]]
            treatment = row[header_map["treatment"]]

            sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(row[header_map["sample_id"]], lab, output_doc)

            sample_doc[SampleConstants.REFERENCE_SAMPLE_ID] = namespace_sample_id(row[header_map["parent_id"]], lab, output_doc)

            sample_doc[SampleConstants.STRAIN] = create_mapped_name(experiment_id, strain, strain, lab, sbh_query, strain=True)

            sample_doc[SampleConstants.REPLICATE] = int(replicate)

            m_time = None

            if len(treatment) > 0:

                treatment_concentration = row[header_map["treatment_concentration"]]
                treatment_concentration_unit = row[header_map["treatment_concentration_unit"]]

                if treatment == "heat":
                    if treatment_concentration_unit == "C":
                        sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(treatment_concentration+":celsius")
                    else:
                        raise ValueError("Unknown temperature {}".format(treatment_concentration_unit))
                else:
                    contents_append_value = create_media_component(experiment_id, treatment, treatment, lab, sbh_query, treatment_concentration + ":" + treatment_concentration_unit)
                    contents.append(contents_append_value)

            treatment_time = row[header_map["treatment_time"]]
            treatment_time_unit = row[header_map["treatment_time_unit"]]

            # normalize to hours
            if treatment_time_unit in ["minute", "minutes"]:
                treatment_time = float(treatment_time)/60.0
                treatment_time_unit = "hour"

            if len(treatment_time_unit) > 0:
                m_time = create_value_unit(str(treatment_time) + ":" + treatment_time_unit)

            # controls
            strain_class = row[header_map["strain_class"]]
            control_type = row[header_map["control_type"]]

            if strain_class == "Control" and control_type == "Negative":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
            if strain_class == "Process":
                if control_type == SampleConstants.STANDARD_BEAD_FLUORESCENCE:
                    sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_BEAD_FLUORESCENCE
                    sample_doc[SampleConstants.STANDARD_ATTRIBUTES] = {}
                    sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_MODEL] = DEFAULT_BEAD_MODEL
                    sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_BATCH] = DEFAULT_BEAD_BATCH
                elif control_type == SampleConstants.STANDARD_BEAD_SIZE:
                    sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_BEAD_SIZE

            # Styox
            if not is_cfu:
                sytox_color = row[header_map["sytox_color"]]
                if len(sytox_color) > 0:
                    # concentration
                    contents.append(create_media_component(experiment_id, "Sytox", "Sytox", lab, sbh_query, row[header_map["sytox_concentration"]] + ":" + row[header_map["sytox_concentration_unit"]]))

                    #color
                    sytox_color_content = create_media_component(experiment_id, "Sytox_color", "Sytox_color", lab, sbh_query)
                    sytox_color_content["value"] = sytox_color
                    contents.append(sytox_color_content)

            # Default Media
            yepd_media = create_media_component(experiment_id, "Media", "Media", lab, sbh_query)
            yepd_media["value"] = "YEPD"
            contents.append(yepd_media)

            if len(contents) > 0:
                sample_doc[SampleConstants.CONTENTS] = contents


            if not SampleConstants.TEMPERATURE in sample_doc:
                # default if not specified
                sample_doc[SampleConstants.TEMPERATURE] = create_value_unit("22:celsius")

            measurement_doc = {}
            measurement_doc[SampleConstants.FILES] = []
            if is_cfu:
                measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_CFU
            else:
                measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_FLOW
                measurement_doc[SampleConstants.M_CHANNELS] = cytometer_channels
                # add default duke cytometer configuration
                if SampleConstants.CYTOMETER_CONFIG not in output_doc:
                    output_doc[SampleConstants.CYTOMETER_CONFIG] = duke_cytometer_configuration_object

            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(1, lab, sample_doc, output_doc)
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(measurement_doc[SampleConstants.MEASUREMENT_TYPE] + "_1", lab, sample_doc, output_doc)

            if m_time is not None:
                measurement_doc[SampleConstants.TIMEPOINT] = m_time

            #CFU 305
            #culture_cells_ml 2.33E+07
            #estimated_cells_plated 583
            #estimated_cells/ml 1.22E+07
            #percent_killed 47.60%
            #date_of_experiment 6/10/20
            cfu_data = {}
            if is_cfu:
                if len(row[header_map["CFU"]]) > 0:
                    cfu_data[headers[header_map["CFU"]]] = int(float(row[header_map["CFU"]]))
                cfu_data[headers[header_map["culture_cells/ml"]]] = int(float(row[header_map["culture_cells/ml"]]))
                cfu_data[headers[header_map["estimated_cells_plated"]]] = int(row[header_map["estimated_cells_plated"]])
                cfu_data[headers[header_map["estimated_cells/ml"]]] = int(float(row[header_map["estimated_cells/ml"]]))
                cfu_data[headers[header_map["percent_killed"]]] = float(row[header_map["percent_killed"]])
                cfu_data[headers[header_map["date_of_experiment"]]] = datetime.datetime.strptime(row[header_map["date_of_experiment"]], doe_format).strftime(doe_format)
            else:
                #culture_cells/ml
                #date_of_experiment
                if len(row[header_map["culture_cells/ml"]]) > 0:
                    cfu_data[headers[header_map["culture_cells/ml"]]] = int(float(row[header_map["culture_cells/ml"]]))
                cfu_data[headers[header_map["date_of_experiment"]]] = datetime.datetime.strptime(row[header_map["date_of_experiment"]], doe_format).strftime(doe_format)

            measurement_doc["cfu_data"] = cfu_data

            file_id = namespace_file_id(1, lab, measurement_doc, output_doc)
            if is_cfu:
                file_type = SampleConstants.infer_file_type(input_file)
                measurement_doc[SampleConstants.FILES].append(
                    {SampleConstants.M_NAME: experiment_id_bak + "__cfu_and_meta.csv",
                     SampleConstants.M_TYPE: file_type,
                     SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
                     SampleConstants.FILE_ID: file_id,
                     SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})
            else:
                filename = row[header_map["fcs_filename"]]
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
