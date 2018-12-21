#!/usr/bin/python
import json
import sys
import os
import six
import collections

from jsonschema import validate
from jsonschema import ValidationError
# Hack hack
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common import SampleConstants
from common import namespace_sample_id, namespace_file_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *
from sbol import *
from .mappings import SampleContentsFilter
from datacatalog.agavehelpers import AgaveHelper

def convert_ginkgo(schema_file, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # default values for FCS support; replace with trace information as available
    DEFAULT_BEAD_MODEL = "SpheroTech URCP-38-2K"
    DEFAULT_BEAD_BATCH = "AJ02"
    DEFAULT_CYTOMETER_CHANNELS = ["SSC - Area", "FSC - Area", "YFP - Area"]
    DEFAULT_CYTOMETER_CONFIGURATION = "agave://data-sd2e-community/ginkgo/instruments/SA3800-20180912.json"

    # For inference
    # Novel Chassis Nand
    NC_WF_ID = "13893_13904"
    # YeastStates gRNA
    YS_WF_ID = "15724"

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)

    schema = json.load(open(schema_file))
    ginkgo_doc = json.load(open(input_file))

    output_doc = {}

    lab = SampleConstants.LAB_GINKGO

    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []
    samples_w_data = 0

    if "experimental_reference" in ginkgo_doc:
        output_doc[SampleConstants.EXPERIMENT_REFERENCE] = ginkgo_doc["experimental_reference"]
        map_experiment_reference(config, output_doc)

    if "internal_workflow_id" in ginkgo_doc:
        list_of_wf_ids = ginkgo_doc["internal_workflow_id"]
        experiment_id = '.'.join(str(wf_id) for wf_id in list_of_wf_ids)
        output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(experiment_id, lab)

    if "samples" in ginkgo_doc:
        ginkgo_iterator = ginkgo_doc["samples"]
    else:
        ginkgo_iterator = ginkgo_doc

    for ginkgo_sample in ginkgo_iterator:
        sample_doc = {}
        #sample_doc[SampleConstants.SAMPLE_ID] = str(ginkgo_sample["sample_id"])
        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(str(ginkgo_sample["sample_id"]), lab)

        contents = []
        for reagent in ginkgo_sample["content"]["reagent"]:

            reagent_id = reagent["id"]
            if int(reagent_id) not in SampleContentsFilter.GINKGO_LAB_IDS:
                reagent_name = reagent["name"]
                concentration_prop = "concentration"
                if concentration_prop in reagent:
                    contents.append(create_media_component(output_doc.get(SampleConstants.EXPERIMENT_ID, "not bound yet"), reagent_name, reagent_id, lab, sbh_query, reagent[concentration_prop]))
                else:
                    contents.append(create_media_component(output_doc.get(SampleConstants.EXPERIMENT_ID, "not bound yet"), reagent_name, reagent_id, lab, sbh_query))

        # It's possible to have no reagents if they're all skipped
        # per the filter.
        if len(contents) > 0:
            sample_doc[SampleConstants.CONTENTS] = contents

        for strain in ginkgo_sample["content"]["strain"]:
            # this can either be a dict or an int
            strain_name = None
            strain_id = None
            if type(strain) == int:
                strain_name = str(strain)
                strain_id = str(strain)
            elif isinstance(strain, collections.Mapping):
                strain_name = strain["name"]
                strain_id = strain["id"]
            else:
                raise ValueError("Strain is not an integer or a dictionary: {}".format(strain))

            sample_doc[SampleConstants.STRAIN] = create_mapped_name(output_doc.get(SampleConstants.EXPERIMENT_ID, "not bound yet"), strain_name, strain_id, lab, sbh_query, strain=True)
            # TODO multiple strains?
            continue

        if "molecule" in ginkgo_sample["content"]:
            for molecule in ginkgo_sample["content"]["molecule"]:
                sample_doc[SampleConstants.GENETIC_CONSTRUCT] = create_mapped_name(output_doc.get(SampleConstants.EXPERIMENT_ID, "not bound yet"), molecule["name"], molecule["id"], lab, sbh_query, strain=False)
                # TODO multiple genetic constructs?
                continue

        props = ginkgo_sample["properties"]

        # map standard for, type,
        if SampleConstants.STANDARD_TYPE in ginkgo_sample:
            sample_doc[SampleConstants.STANDARD_TYPE] = ginkgo_sample[SampleConstants.STANDARD_TYPE]
        if SampleConstants.STANDARD_FOR in ginkgo_sample:
            standard_for_val = ginkgo_sample[SampleConstants.STANDARD_FOR]
            # int -> str conversion
            if isinstance(standard_for_val, list):
                if type(standard_for_val[0]) == int:
                    standard_for_val = [str(n) for n in standard_for_val]

            sample_doc[SampleConstants.STANDARD_FOR] = standard_for_val

        # map control for, type
        if SampleConstants.CONTROL_TYPE in ginkgo_sample:
            control_type = ginkgo_sample[SampleConstants.CONTROL_TYPE]
            # Ginkgo's value - map to enum
            if control_type == "BASELINE_media_only_control_for_platereader":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_BASELINE_MEDIA_PR
            else:
                sample_doc[SampleConstants.CONTROL_TYPE] = control_type
        if SampleConstants.CONTROL_FOR in ginkgo_sample:
            control_for_val = ginkgo_sample[SampleConstants.CONTROL_FOR]
            # int -> str conversion
            if isinstance(control_for_val, list):
                if type(control_for_val[0]) == int:
                    control_for_val = [str(n) for n in control_for_val]

            sample_doc[SampleConstants.CONTROL_FOR] = control_for_val

        # fill in attributes if we have a bead standard
        if SampleConstants.STANDARD_TYPE in sample_doc and \
            sample_doc[SampleConstants.STANDARD_TYPE] == SampleConstants.STANDARD_BEAD_FLUORESCENCE and \
                SampleConstants.STANDARD_ATTRIBUTES not in sample_doc:
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES] = {}
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_MODEL] = DEFAULT_BEAD_MODEL
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_BATCH] = DEFAULT_BEAD_BATCH


        # do some cleaning
        temp_prop = "SD2_incubation_temperature"

        if temp_prop in props:
            temperature = props[temp_prop]
            if "centigrade" in temperature:
                temperature = temperature.replace("centigrade", "celsius")
            sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(temperature)

        replicate_prop = "SD2_replicate"
        if replicate_prop in props:
            replicate_val = props[replicate_prop]
            if isinstance(replicate_val, six.string_types):
                # Ginkgo sometimes sends floats here.
                replicate_val_f = float(replicate_val)
                replicate_val = int(replicate_val_f)
            sample_doc[SampleConstants.REPLICATE] = replicate_val

        tx_sample_prop = "SD2_TX_sample_id"
        if tx_sample_prop in props:
            # pull out the aliquot id and namespace it for TX
            # e.g. aq1bszwpwmtqux/ct1bsxfcxdqw55
            sample_doc[SampleConstants.REFERENCE_SAMPLE_ID] = namespace_sample_id(props[tx_sample_prop].split("/")[0], SampleConstants.LAB_TX)

        # determinstically derive measurement ids from sample_id + counter (local to sample)
        measurement_counter = 1

        ginkgo_measurements = ginkgo_sample["measurements"]
        # pre-scan for library prep
        # The larger measurement ID number corresponds to the miniaturized protocol
        library_prep = []
        for measurement_key in ginkgo_measurements.keys():
            assay_type = ginkgo_measurements[measurement_key]["assay_type"]
            if assay_type == "NGS (RNA)":
                i_measurement_key = int(measurement_key)
                library_prep.append(i_measurement_key)
        prep_len = len(library_prep)
        library_prep_dict = {}
        if prep_len == 2:
            library_prep = sorted(library_prep)
            for index, library_prep_key in enumerate(library_prep):
                s_library_prep_key = str(library_prep_key)
                if index == 0:
                    library_prep_dict[s_library_prep_key] = SampleConstants.MEASUREMENT_LIBRARY_PREP_NORMAL
                elif index == 1:
                    library_prep_dict[s_library_prep_key] = SampleConstants.MEASUREMENT_LIBRARY_PREP_MINIATURIZED
        elif prep_len == 1:
            library_prep_dict[str(library_prep[0])] = SampleConstants.MEASUREMENT_LIBRARY_PREP_NORMAL
        elif prep_len > 2:
            raise ValueError("Library prep issue: more than 2 RNASeq runs?")

        for measurement_key in ginkgo_measurements.keys():
            measurement_doc = {}

            if measurement_key in library_prep_dict:
                measurement_doc[SampleConstants.MEASUREMENT_LIBRARY_PREP] = library_prep_dict[measurement_key]

            time_prop = "SD2_timepoint"
            if time_prop in props:
                time_val = props[time_prop]
                if time_val == "pre-pre-induction":
                    print("Warning: time val is not discrete, replacing fixed value!".format(time_val))
                    time_val = "-3:hour"
                elif time_val == "pre-induction":
                    print("Warning: time val is not discrete, replacing fixed value!".format(time_val))
                    time_val = "0:hour"

                # more cleanup
                if time_val.endswith("hours"):
                    time_val = time_val.replace("hours", "hour")
                measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time_val)

            measurement_doc[SampleConstants.FILES] = []

            measurement_props = ginkgo_measurements[measurement_key]

            assay_type = measurement_props["assay_type"]
            if assay_type == "NGS (RNA)":
                measurement_type = SampleConstants.MT_RNA_SEQ
            elif assay_type == "FACS":
                measurement_type = SampleConstants.MT_FLOW
            elif assay_type == "Plate Reader Assay":
                measurement_type = SampleConstants.MT_PLATE_READER
            elif assay_type == "Global Proteomics":
                measurement_type = SampleConstants.MT_PROTEOMICS
            elif assay_type == "NGS (Genome)":
                measurement_type = SampleConstants.MT_DNA_SEQ
            else:
                raise ValueError("Could not parse MT: {}".format(assay_type))

            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type
            measurement_doc[SampleConstants.MEASUREMENT_NAME] = measurement_props["measurement_name"]

            # use measurement_name to do some inference if we have no challenge problem, yet
            # (could be superceded later)
            # FIXME update this later; Ginkgo needs to provide this
            if SampleConstants.CHALLENGE_PROBLEM not in output_doc:
                measurement_name = measurement_doc[SampleConstants.MEASUREMENT_NAME]
                if measurement_name == "NC E. coli NAND 37C (WF: 13893, SEQ_WF: 14853)" or \
                   measurement_name == "NC E. coli NAND 30C (WF: 13904, SEQ_WF: 14853)" or \
                   measurement_name == "s27 Global Proteomics with Relative Quantification for w14096 (QE HF-X)" or \
                   measurement_name == "NC NAND Platereader re-upload" or \
                   measurement_name == "NC NAND Platereader":
                    print("Setting Novel Chassis Challenge Problem by Inference")
                    output_doc[SampleConstants.CHALLENGE_PROBLEM] = SampleConstants.CP_NOVEL_CHASSIS
                    # workflow id from ginkgo
                    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(NC_WF_ID, lab)
                    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = "NovelChassis-NAND-Gate"
                    # fill in URI
                    map_experiment_reference(config, output_doc)
                elif measurement_name == "P63 Received Aug 2018 (WF: 15724, SEQ_WF: 16402)":
                    print("Setting Yeast Gates Challenge Problem by Inference")
                    output_doc[SampleConstants.CHALLENGE_PROBLEM] = SampleConstants.CP_YEAST_GATES
                    # workflow id from ginkgo
                    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(YS_WF_ID, lab)
                    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = "YeastSTATES-gRNA-Seq-Diagnosis"
                    # fill in URI
                    map_experiment_reference(config, output_doc)
                else:
                    # We should force a failure here. If we can't identify the challenge problem
                    # or experiment id, this trace becomes very difficult to search for
                    raise ValueError("Cannot identify challenge problem: {}".format(ginkgo_sample))

            # generate a measurement id unique to this sample
            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(".".join([sample_doc[SampleConstants.SAMPLE_ID], str(measurement_counter)]), output_doc[SampleConstants.LAB])

            # record a measurement grouping id to find other linked samples and files
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(measurement_key, output_doc[SampleConstants.LAB])

            measurement_counter = measurement_counter + 1

            tmt_prop = "TMT_channel"
            if tmt_prop in measurement_props:
                tmt_val = measurement_props[tmt_prop]
                if SampleConstants.SAMPLE_TMT_CHANNEL not in sample_doc:
                    sample_doc[SampleConstants.SAMPLE_TMT_CHANNEL] = tmt_val
                else:
                    if sample_doc[SampleConstants.SAMPLE_TMT_CHANNEL] != tmt_val:
                        raise ValueError("Multiple TMT channels for sample?: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))

            # apply defaults, if nothing mapped
            if measurement_type == SampleConstants.MT_FLOW:
                if SampleConstants.M_CHANNELS not in measurement_doc:
                    measurement_doc[SampleConstants.M_CHANNELS] = DEFAULT_CYTOMETER_CHANNELS
                if SampleConstants.M_INSTRUMENT_CONFIGURATION not in measurement_doc:
                    measurement_doc[SampleConstants.M_INSTRUMENT_CONFIGURATION] = DEFAULT_CYTOMETER_CONFIGURATION

            # Use default NC negative strain, if CP matches
            # Match on lab ID for now, as this is unambiguous given dictionary name changes
            # do the same thing for positive control
            if SampleConstants.CONTROL_TYPE not in sample_doc and \
                SampleConstants.STRAIN in sample_doc and \
                    output_doc[SampleConstants.CHALLENGE_PROBLEM] == SampleConstants.CP_NOVEL_CHASSIS:
                if sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("194568", output_doc[SampleConstants.LAB]):
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
                elif sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("194575", output_doc[SampleConstants.LAB]):
                    # ON without IPTG, OFF with IPTG, plasmid (high level)
                    # we also need to indicate the control channels for the fluorescence control
                    # this is not known by the lab typically, has to be provided externally
                    if SampleConstants.CONTENTS not in sample_doc:
                        sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                        sample_doc[SampleConstants.CONTROL_CHANNEL] = "YFP - Area"
                    else:
                        found = False
                        for content in sample_doc[SampleConstants.CONTENTS]:
                            if SampleConstants.NAME in content and SampleConstants.LABEL in content[SampleConstants.NAME]:
                                content_label = content[SampleConstants.NAME][SampleConstants.LABEL]
                                if content_label == "IPTG":
                                    found = True
                        if not found:
                            sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                            sample_doc[SampleConstants.CONTROL_CHANNEL] = "YFP - Area"

            file_counter = 1
            for key in measurement_props["dataset_files"].keys():
                if key == "processed":
                    for processed in measurement_props["dataset_files"]["processed"]:
                        for sub_processed in processed:
                            file_id = namespace_file_id(".".join([sample_doc[SampleConstants.SAMPLE_ID], str(measurement_counter), str(file_counter)]), output_doc[SampleConstants.LAB])

                            file_type = SampleConstants.infer_file_type(sub_processed)
                            measurement_doc[SampleConstants.FILES].append(
                                {SampleConstants.M_NAME: sub_processed,
                                 SampleConstants.M_TYPE: file_type,
                                 SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_PROCESSED],
                                 SampleConstants.FILE_ID: file_id,
                                 SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})
                            file_counter = file_counter + 1
                elif key == "raw":
                    for raw in measurement_props["dataset_files"]["raw"]:
                        for sub_raw in raw:
                            file_id = namespace_file_id(".".join([sample_doc[SampleConstants.SAMPLE_ID], str(measurement_counter), str(file_counter)]), output_doc[SampleConstants.LAB])

                            file_type = SampleConstants.infer_file_type(sub_raw)
                            measurement_doc[SampleConstants.FILES].append(
                                {SampleConstants.M_NAME: sub_raw,
                                 SampleConstants.M_TYPE: file_type,
                                 SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
                                 SampleConstants.FILE_ID: file_id,
                                 SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})
                            file_counter = file_counter + 1
                else:
                    raise ValueError("Unknown measurement type: {}".format(key))

            if SampleConstants.MEASUREMENTS not in sample_doc:
                sample_doc[SampleConstants.MEASUREMENTS] = []
            sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)
            samples_w_data = samples_w_data + 1
            #print('sample {} / measurement {} contains {} files'.format(sample_doc[SampleConstants.SAMPLE_ID], measurement_key, len(measurement_doc[SampleConstants.FILES])))

        if SampleConstants.MEASUREMENTS not in sample_doc:
            sample_doc[SampleConstants.MEASUREMENTS] = []
        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    print('Samples in file: {}'.format(len(ginkgo_iterator)))
    print('Samples with data: {}'.format(samples_w_data))

    try:
        validate(output_doc, schema)
        # if verbose:
        #print(json.dumps(output_doc, indent=4))
        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join(
                    "output/ginkgo", os.path.basename(input_file))
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
                convert_ginkgo(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_ginkgo(sys.argv[1], sys.argv[2])
