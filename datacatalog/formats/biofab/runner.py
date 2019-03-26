#!/usr/bin/python
import json
import sys
import os
import six
from jq import jq
from jsonschema import validate, ValidationError
from sbol import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *
from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id

# common across methods
attributes_attr = "attributes"
replicate_attr = "replicate"
sample_attr = "sample"
timepoint_attr = "timepoint"
sample_id_attr = "sample_id"
sample_name_attr = "sample_name"
op_id = "operation_id"
job_id = "job_id"
type_attr = "type"
type_of_media_attr = "type_of_media"
part_of_attr = "part_of"
source_attr = "sources"
item_id_attr = "item_id"
media_attr = "media"
inducer_attr = "inducer"
experimental_media_attr = "experimental_media"
experimental_antibiotic_attr = "experimental_antibiotic"
concentration_attr = "concentration"
volume_attr = "volume"
od600_attr = "od600"
control_attr = "control"
standard_attr = "standard"
lot_attr = "Lot No."

negative_control = False
is_sytox = False

DEFAULT_BEAD_MODEL = "SpheroTech URCP-38-2K"
SYTOX_DEFAULT_CYTOMETER_CHANNELS = ["FSC-A", "SSC-A", "FL1-A", "FL4-A"]
NO_SYTOX_DEFAULT_CYTOMETER_CHANNELS = ["FSC-A", "SSC-A", "FL1-A"]

DEFAULT_CYTOMETER_CONFIGURATION = "agave://data-sd2e-community/biofab/instruments/accuri/5539/11202018/cytometer_configuration.json"

def add_input_media(original_experiment_id, lab, sbh_query, reagents, biofab_doc, item):
    try:
        media_value = jq(".operations[].inputs[] | select (.name | contains (\"Type of Media\")).value").transform(biofab_doc)
    except StopIteration:
        print("Warning, could not find media for {}".format(item))
        media_value = None
    if media_value is not None:
        reagents.append(create_media_component(original_experiment_id, media_value, media_value, lab, sbh_query))

def add_file_no_source(biofab_sample, output_doc, config, lab, original_experiment_id, measurement_type):

    operation_id = None
    # won't have a sample here; construct one out of the
    # operation and file id
    if "generated_by" in biofab_sample and "operations" in biofab_sample["generated_by"]:
        operation_id = biofab_sample["generated_by"]["operations"][0]
    elif "generated_by" in biofab_sample and "operation_id" in biofab_sample["generated_by"]:
        operation_id = biofab_sample["generated_by"]["operation_id"]
    else:
        print("Warning, could not parse operation id, skipping")
        return

    file_id = None
    if "file_id" in biofab_sample:
        file_id = biofab_sample["file_id"]
    elif "id" in biofab_sample:
        file_id = biofab_sample["id"]
    else:
        raise ValueError("Could not parse file id")

    sample_doc = {}
    sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(operation_id + "_" + file_id, lab, output_doc)
    sample_doc[SampleConstants.LAB_SAMPLE_ID] = namespace_sample_id(operation_id + "_" + file_id, lab, None)

    measurement_doc = {}
    measurement_doc[SampleConstants.FILES] = []

    measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type

    add_measurement_id(measurement_doc, sample_doc, output_doc)

    measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(operation_id, lab, sample_doc, output_doc)

    add_file_name(config, biofab_sample, measurement_doc, original_experiment_id, lab, output_doc)
    add_measurement_doc(measurement_doc, sample_doc, output_doc)

def add_experimental_design(biofab_sample, output_doc, config, lab, original_experiment_id):

    if "filename" in biofab_sample:
        filename = biofab_sample['filename']
        # Special case we are targeting here: is this an experimental design?
        if 'experimental_design' in filename and "generated_by" in biofab_sample and "file_id" in biofab_sample and "operation_id" in biofab_sample["generated_by"]:
            # won't have a sample here; construct one out of the
            # operation and file id
            file_gen = biofab_sample["generated_by"]["operation_id"]
            file_id = biofab_sample["file_id"]

            sample_doc = {}
            sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(file_gen + "_" + file_id, lab, output_doc)
            sample_doc[SampleConstants.LAB_SAMPLE_ID] = namespace_sample_id(file_gen + "_" + file_id, lab, None)

            measurement_doc = {}
            measurement_doc[SampleConstants.FILES] = []

            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_EXPERIMENTAL_DESIGN

            add_measurement_id(measurement_doc, sample_doc, output_doc)
            add_measurement_group_id(measurement_doc, biofab_sample, sample_doc, output_doc)
            add_file_name(config, biofab_sample, measurement_doc, original_experiment_id, lab, output_doc)
            add_measurement_doc(measurement_doc, sample_doc, output_doc)

def add_timepoint(time_val, measurement_doc, input_item_id, biofab_doc):
    if time_val is not None:
        measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time_val)
    elif input_item_id is not None:
        try:
            time_val = jq(".operations[] | select(.inputs[].item_id ==\"" + input_item_id + "\").inputs[] | select (.name == \"Timepoint (hr)\").value").transform(biofab_doc)
            measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time_val + ":hour")
        except StopIteration:
            print("Warning: could not find matching time value for {}".format(input_item_id))

def add_od(item, sample_doc):
    if item is not None and attributes_attr in item and od600_attr in item[attributes_attr]:
        od = item[attributes_attr][od600_attr]
        # this sometimes comes in as a float now
        if isinstance(od, float):
            od = str(od)
        sample_doc[SampleConstants.INOCULATION_DENSITY] = create_value_unit(od + ":" + od600_attr)

def add_control(item, sample_doc, output_doc):
    global negative_control
    if item is not None:
        if attributes_attr in item and control_attr in item[attributes_attr]:
            control_val = item[attributes_attr][control_attr]
            # we also need to indicate the control channels for the fluorescence control
            # this is not known by the lab typically, has to be provided externally
            if control_val == "negative_sytox":
                # have we marked a negative control yet? we can re-use the negative_sytox, which is an unadulterated WT
                if not negative_control:
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
                    negative_control = True
                else:
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_CELL_DEATH_NEG_CONTROL
            elif control_val == "positive_sytox":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_CELL_DEATH_POS_CONTROL
                sample_doc[SampleConstants.CONTROL_CHANNEL] = "FL4-A"
            elif control_val == "positive_gfp":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                sample_doc[SampleConstants.CONTROL_CHANNEL] = "FL1-A"
        elif SampleConstants.STRAIN in sample_doc and output_doc[SampleConstants.CHALLENGE_PROBLEM] == SampleConstants.CP_YEAST_STATES:
            # Biofab does not provide control information for earlier YG plans;
            # Need to drive this from strains (WT and NOR_00)
            if sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("22544", output_doc[SampleConstants.LAB]):
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
            elif sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("6390", output_doc[SampleConstants.LAB]):
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                sample_doc[SampleConstants.CONTROL_CHANNEL] = "FL1-A"

def add_replicate(item, sample_doc):
    if attributes_attr in item and replicate_attr in item[attributes_attr]:
        replicate_val = item[attributes_attr][replicate_attr]
        if isinstance(replicate_val, six.string_types):
            replicate_val = int(replicate_val)
        sample_doc[SampleConstants.REPLICATE] = replicate_val

def add_strain(original_experiment_id, item, sample_doc, lab, sbh_query):
    if sample_attr in item:
        if sample_id_attr not in item[sample_attr]:
            print("Warning, sample is missing a strain entry: {}".format(item))
        else:
            sample_id = item[sample_attr][sample_id_attr]
            strain = item[sample_attr][sample_name_attr]
            sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, strain, sample_id, lab, sbh_query, strain=True)

def get_timepoint_from_item(item):
    if attributes_attr in item and timepoint_attr in item[attributes_attr]:
        return item[attributes_attr][timepoint_attr]
    else:
        return None

def read_bead_fluorescence_from_item(item, sample_doc):
    if attributes_attr in item:
        if standard_attr in item[attributes_attr]:
            standard_val = item[attributes_attr][standard_attr]

            # this is parsed out automatically, but at the plate level, do not use
            if standard_val != "IGEM_protocol":
                sample_doc[SampleConstants.STANDARD_TYPE] = standard_val

        if lot_attr in item[attributes_attr]:
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES] = {}
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_MODEL] = DEFAULT_BEAD_MODEL
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_BATCH] = item[attributes_attr][lot_attr]

# operation id aggregates across files for a single measurement, e.g.
"""
"operation_id": "92240",
"operation_type": {
"operation_type_id": "415",
"category": "Flow Cytometry",
"name": "Flow Cytometry 96 well"
},
"""
# generate a measurement id unique to this sample
# Biofab does not have additional measurements per file, can fix to 1
def add_measurement_id(measurement_doc, sample_doc, output_doc):

    # namespace with experiment id, as sometimes the sample is shared (e.g. bead samples)
    measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id("1", output_doc[SampleConstants.LAB], sample_doc, output_doc)

def add_measurement_group_id(measurement_doc, file, sample_doc, output_doc):
    # record a measurement grouping id to find other linked samples and files
    if "generated_by" not in file:
        print("Warning, cannot find generated_by, skipping file: {}".format(file))
        return
    else:
        file_gen = file["generated_by"]
        mg_val = None
        if op_id in file_gen:
            mg_val = file_gen[op_id]
        elif job_id in file_gen:
            mg_val = file_gen[job_id]
        else:
            raise ValueError("Cannot find measurement group id: {}".format(file))

    measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(mg_val, output_doc[SampleConstants.LAB], sample_doc, output_doc)

def add_measurement_type(file, measurement_doc):

    global is_sytox

    if type_attr in file:
        assay_type = file[type_attr]
        if assay_type == "FCS":
            measurement_type = SampleConstants.MT_FLOW
            if SampleConstants.M_CHANNELS not in measurement_doc:
                if is_sytox:
                    measurement_doc[SampleConstants.M_CHANNELS] = SYTOX_DEFAULT_CYTOMETER_CHANNELS
                else:
                    measurement_doc[SampleConstants.M_CHANNELS] = NO_SYTOX_DEFAULT_CYTOMETER_CHANNELS
            if SampleConstants.M_INSTRUMENT_CONFIGURATION not in measurement_doc:
                measurement_doc[SampleConstants.M_INSTRUMENT_CONFIGURATION] = DEFAULT_CYTOMETER_CONFIGURATION
        elif assay_type == "CSV":
            measurement_type = SampleConstants.MT_PLATE_READER
        else:
            raise ValueError("Could not parse MT: {}".format(assay_type))
    else:
        # Workaround for biofab; uploaded txts are PR
        # Otherwise the above version of this fails
        # Files that did not have a type
        fn = file['filename'].lower()
        if fn.endswith(".txt"):
            measurement_type = SampleConstants.MT_PLATE_READER
        elif fn.endswith(".fastq.gz"):
            measurement_type = SampleConstants.MT_RNA_SEQ
        elif fn.endswith(".ab1"):
            measurement_type = SampleConstants.MT_SEQUENCING_CHROMATOGRAM
        elif fn.endswith("jpg"):
            measurement_type = SampleConstants.MT_IMAGE
        else:
            raise ValueError("Could not parse FT: {}".format(file['filename']))

    measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type

def add_measurement_doc(measurement_doc, sample_doc, output_doc):

    if SampleConstants.MEASUREMENTS not in sample_doc:
        sample_doc[SampleConstants.MEASUREMENTS] = []
    sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)

    # NC Specific Channels
    if output_doc[SampleConstants.CHALLENGE_PROBLEM] == SampleConstants.CP_NOVEL_CHASSIS and \
            measurement_doc[SampleConstants.MEASUREMENT_TYPE] == SampleConstants.MT_FLOW:
        measurement_doc[SampleConstants.M_CHANNELS] = ["FSC-A", "SSC-A", "FL1-A"]

    # NC does not provide control mappings
    # Use the default NC negative strain, if CP matches
    # Match on lab ID for now, as this is unambiguous given dictionary common name changes
    # do the same thing for positive control
    if SampleConstants.CONTROL_TYPE not in sample_doc and \
        SampleConstants.STRAIN in sample_doc and \
            output_doc[SampleConstants.CHALLENGE_PROBLEM] == SampleConstants.CP_NOVEL_CHASSIS:
        if sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("8", output_doc[SampleConstants.LAB]):
            sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
        elif sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("23382", output_doc[SampleConstants.LAB]):
            # ON without IPTG, OFF with IPTG, plasmid (high level)
            # we also need to indicate the control channels for the fluorescence control
            # this is not known by the lab typically, has to be provided externally
            if SampleConstants.CONTENTS not in sample_doc:
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                sample_doc[SampleConstants.CONTROL_CHANNEL] = "FL1-A"
            else:
                found = False
                for content in sample_doc[SampleConstants.CONTENTS]:
                    if SampleConstants.NAME in content and SampleConstants.LABEL in content[SampleConstants.NAME]:
                        content_label = content[SampleConstants.NAME][SampleConstants.LABEL]
                        if content_label == "IPTG":
                            found = True
                if not found:
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                    sample_doc[SampleConstants.CONTROL_CHANNEL] = "FL1-A"

    output_doc[SampleConstants.SAMPLES].append(sample_doc)

def add_file_name(config, file, measurement_doc, original_experiment_id, lab, output_doc):
    if config.get('extend', False):
        file_name = extend_biofab_filename(
            file['filename'], original_experiment_id, file['generated_by'])
    else:
        file_name = file["filename"]

    file_id = file.get('file_id', None)
    # biofab stores this in multiple ways
    if file_id is None:
        file_id = file.get('id', None)
        # these are localized _per_ run, namespace using exp_id
        file_id = '.'.join([original_experiment_id, file_id])

    if file_id is None:
        raise ValueError("Could not parse file id? {}".format(file_id))
    elif file_id is not None:
        file_id = namespace_file_id(file_id, lab, measurement_doc, output_doc)

    file_type = SampleConstants.infer_file_type(file_name)
    measurement_doc[SampleConstants.FILES].append(
        {SampleConstants.M_NAME: file_name,
         SampleConstants.M_TYPE: file_type,
         SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
         SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0,
         SampleConstants.FILE_ID: file_id})

def extend_biofab_filename(file_name, plan_id, generated_by):
    # Add context to the filename while we have enough information to
    # generate it
    gen_id = None
    if 'operation_id' in generated_by:
        gen_id = 'op_' + generated_by['operation_id']
    elif 'job_id' in generated_by:
        gen_id = 'job_' + generated_by['job_id']
    else:
        gen_id = 'unknown'
    return '/'.join([str(plan_id), gen_id, file_name])

def add_inducer_experimental_media(original_experiment_id, item, lab, sbh_query, reagents, biofab_doc):
    # no media attribute, try to look up through the last source
    if source_attr in item:
        last_source_ = item[source_attr][0]
        last_source_lookup = jq(".items[] | select(.item_id==\"" + last_source_ + "\")").transform(biofab_doc)
        if attributes_attr in last_source_lookup:
            found_inducer_media = False
            for inducer_media_attr in [experimental_media_attr, inducer_attr]:
                if found_inducer_media:
                    continue
                if inducer_media_attr in last_source_lookup[attributes_attr]:
                    combined_inducer = last_source_lookup[attributes_attr][inducer_media_attr]
                    if combined_inducer != "None":
                        # "IPTG_0.25|arab_25.0"
                        combined_inducer_split = combined_inducer.split("|")
                        found_inducer_media = True
                        for inducer in combined_inducer_split:
                            inducer_split = inducer.split("_")
                            # there are a large number of edge cases here - nones appear everywhere in the latest 17016 trace
                            if len(inducer_split) == 2:
                                if inducer_split[1] == "None":
                                    if inducer_split[0] != "None":
                                        reagents.append(create_media_component(original_experiment_id, inducer_split[0], inducer_split[0], lab, sbh_query))
                                else:
                                    if inducer_split[0] != "None":
                                        reagents.append(create_media_component(original_experiment_id, inducer_split[0], inducer_split[0], lab, sbh_query, inducer_split[1]))
                            else:
                                # now we have something unexpected like None_arab_25.0 or Kan_arab_25.0
                                # and have to carefully try and figure out the legal pairs
                                seen_index = set()
                                for index, sub_inducer_split in enumerate(inducer_split):
                                    if index in seen_index:
                                        continue
                                    if sub_inducer_split == "None":
                                        seen_index.add(index)
                                    else:
                                        if index + 1 < len(inducer_split):
                                            val1 = inducer_split[index]
                                            val2 = inducer_split[index + 1]
                                            try:
                                                float(val2)
                                                # arab_25.0
                                                reagents.append(create_media_component(original_experiment_id, val1, val1, lab, sbh_query, val2))
                                                seen_index.add(index)
                                                seen_index.add(index + 1)
                                            except ValueError:
                                                # Kan
                                                reagents.append(create_media_component(original_experiment_id, val1, val1, lab, sbh_query))
                                                seen_index.add(index)
                                        else:
                                            # Kan
                                            val1 = inducer_split[index]
                                            reagents.append(create_media_component(original_experiment_id, val1, val1, lab, sbh_query))
                                            seen_index.add(index)
            if experimental_antibiotic_attr in last_source_lookup[attributes_attr]:
                if not found_inducer_media:
                    experimental_antibiotic = last_source_lookup[attributes_attr][experimental_antibiotic_attr]
                    if experimental_antibiotic != "None":
                        reagents.append(create_media_component(original_experiment_id, experimental_antibiotic, experimental_antibiotic, lab, sbh_query))

def convert_biofab(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    biofab_doc = json.load(open(input_file, encoding=encoding))

    output_doc = {}

    lab = SampleConstants.LAB_UWBF

    original_experiment_id = biofab_doc["plan_id"]
    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(biofab_doc["plan_id"], lab)
    output_doc[SampleConstants.CHALLENGE_PROBLEM] = biofab_doc.get("attributes", {}).get("challenge_problem")
    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = biofab_doc.get(
        "attributes", {}).get("experiment_reference")

    map_experiment_reference(config, output_doc)

    output_doc[SampleConstants.LAB] = biofab_doc.get("attributes", {}).get("lab", lab)
    output_doc[SampleConstants.SAMPLES] = []

    # is this a Sytox plan? Per:
    # Biofab has a mix of Sytox and Non-Sytox YS plans.
    # We need to peek ahead, as this affects FCS channel mappings
    global is_sytox
    try:
        sytox_found = jq(".items[] | select (.attributes.control == \"positive_sytox\")").transform(biofab_doc)
        if sytox_found is not None and len(sytox_found) > 0:
            print(sytox_found)
            print("Sytox found for plan: {}".format(original_experiment_id))
            is_sytox = True
        else:
            print("No Sytox found for plan: {}".format(original_experiment_id))
            is_sytox = False
    except StopIteration:
        print("Warning, could not find sytox control for plan: {}".format(original_experiment_id))

    missing_part_of_items = set()

    # process bottom up from file -> sample
    for biofab_sample in biofab_doc["files"]:
        sample_doc = {}
        if source_attr not in biofab_sample:
            print("Warning, file is missing a source {}".format(biofab_sample))
            # experimental design is a special case
            if type_attr in biofab_sample and biofab_sample[type_attr] == "FCS":
                print("Trying to resolve as an FCS file with no source")
                add_file_no_source(biofab_sample, output_doc, config, lab, original_experiment_id, SampleConstants.MT_FLOW)
            elif type_attr in biofab_sample and biofab_sample[type_attr] == "CSV" and "filename" in biofab_sample and "experimental_design" not in biofab_sample["filename"]:
                print("Trying to resolve as a CSV file with no source")
                add_file_no_source(biofab_sample, output_doc, config, lab, original_experiment_id, SampleConstants.MT_PLATE_READER)
            elif "filename" in biofab_sample and biofab_sample["filename"].endswith(".ab1"):
                print("Trying to resolve as an ab1 file with no source")
                add_file_no_source(biofab_sample, output_doc, config, lab, original_experiment_id, SampleConstants.MT_SEQUENCING_CHROMATOGRAM)
            else:
                print("Trying to resolve as an experimental design")
                add_experimental_design(biofab_sample, output_doc, config, lab, original_experiment_id)
            continue
        file_source = biofab_sample[source_attr][0]
        # sample_doc[SampleConstants.SAMPLE_ID] = file_source
        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(file_source, lab, output_doc)
        sample_doc[SampleConstants.LAB_SAMPLE_ID] = namespace_sample_id(file_source, lab, None)

        item = jq(".items[] | select(.item_id==\"" + file_source + "\")").transform(biofab_doc)

        time_val = get_timepoint_from_item(item)

        # plate this source is a part of?
        plate = None
        found_plate = False
        part_of = None
        if part_of_attr not in item:

            if attributes_attr in item and type_of_media_attr in item[attributes_attr]:
                # use ourself instead of doing part_of
                plate = item
                found_plate = True
                part_of = file_source
            else:
                # lookup provenance not resolving, handle this top down, below
                # (PlateReader in particular does this)
                # Special case for FCS files: some plans attach these to the
                # plate, which causes lots of issues. Skip these.
                if type_attr in biofab_sample and biofab_sample[type_attr] == "FCS":
                    lookup_source = jq(".items[] | select(.item_id==\"" + file_source + "\")").transform(biofab_doc)
                    if type_attr in lookup_source and lookup_source[type_attr] == "collection":
                        print("Skipping non-sample FCS source: {}".format(file_source))
                    else:
                        print("Adding non-sample FCS source: {}".format(file_source))
                        missing_part_of_items.add(file_source)
                else:
                    missing_part_of_items.add(file_source)
                continue
        else:
            part_of = item[part_of_attr]
            plate = jq(".items[] | select(.item_id==\"" + part_of + "\")").transform(biofab_doc)

        reagents = []

        plate_source_lookup = None
        plate_source = None
        # one additional lookup
        if found_plate:
            plate_source = plate[source_attr][0]
            plate_source_lookup = plate
        else:
            plate_source = plate[source_attr][0]
            plate_source_lookup = jq(".items[] | select(.item_id==\"" + plate_source + "\")").transform(biofab_doc)

        if type_of_media_attr in plate_source_lookup[attributes_attr] and source_attr not in item:
            media_name = plate_source_lookup[attributes_attr][type_of_media_attr]
            # case for old files that do not have this.
            reagents.append(create_media_component(original_experiment_id, media_name, media_name, lab, sbh_query))
        else:
            if source_attr not in item:
                print("Warning, item is missing a source {}".format(item))
            else:
                # need to follow *another* source chain to find the media_id
                media_source_lookup = None
                media_source_ = item[source_attr][0]
                media_source_lookup = jq(".items[] | select(.item_id==\"" + media_source_ + "\")").transform(biofab_doc)

                if attributes_attr in media_source_lookup and media_attr in media_source_lookup[attributes_attr]:
                    if sample_id_attr in media_source_lookup[attributes_attr][media_attr]:
                        media_id = media_source_lookup[attributes_attr][media_attr][sample_id_attr]
                        reagents.append(create_media_component(original_experiment_id, media_id, media_id, lab, sbh_query))
                    else:
                        raise ValueError("No media id? {}".format(media_source_lookup))
                else:
                    add_inducer_experimental_media(original_experiment_id, media_source_lookup, lab, sbh_query, reagents, biofab_doc)
                    # Alternative: lookup media by inputs
                    add_input_media(original_experiment_id, lab, sbh_query, reagents, biofab_doc, media_source_lookup)

                add_od(media_source_lookup, sample_doc)

                add_control(media_source_lookup, sample_doc, output_doc)

        if "growth_temperature" in plate_source_lookup:
            temperature = plate_source_lookup["attributes"]["growth_temperature"]
            sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(str(temperature) + ":celsius")
        else:
            try:
                temp_value = jq(".operations[].inputs[] | select (.name | contains (\"Growth Temperature\")).value").transform(biofab_doc)
            except StopIteration:
                print("Warning, could not find temperature for {}".format(original_experiment_id))
                temp_value = None
            if temp_value is not None:
                sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(str(temp_value) + ":celsius")

        if len(reagents) > 0:
            sample_doc[SampleConstants.CONTENTS] = reagents

        # could use ID
        add_strain(original_experiment_id, item, sample_doc, lab, sbh_query)

        add_od(item, sample_doc)

        add_control(item, sample_doc, output_doc)

        add_replicate(item, sample_doc)

        # skip controls for now
        # code from Ginkgo doc...
        """
        control_for_prop = "control_for_samples"
        sbh_uri_prop = "SD2_SBH_URI"
        if control_for_prop in biofab_sample:
            control_for_val = biofab_sample[control_for_prop]

            #int -> str conversion
            if isinstance(control_for_val, list):
                if type(control_for_val[0]) == int:
                    control_for_val = [str(n) for n in control_for_val]

            if sbh_uri_prop in props:
                sbh_uri_val = props[sbh_uri_prop]
                if "fluorescein_control" in sbh_uri_val:
                    sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_FLUORESCEIN
                    sample_doc[SampleConstants.STANDARD_FOR] = control_for_val
                else:
                    print("Unknown control for sample: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
            else:
                print("Unknown control for sample: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
        """
        measurement_doc = {}

        add_timepoint(time_val, measurement_doc, plate_source, biofab_doc)

        measurement_doc[SampleConstants.FILES] = []

        add_measurement_type(biofab_sample, measurement_doc)

        add_measurement_id(measurement_doc, sample_doc, output_doc)

        add_measurement_group_id(measurement_doc, biofab_sample, sample_doc, output_doc)

        add_file_name(config, biofab_sample, measurement_doc, original_experiment_id, lab, output_doc)

        add_measurement_doc(measurement_doc, sample_doc, output_doc)

    # alternate temperate when we lack provenance
    temp_value = None
    if len(missing_part_of_items) > 0:
        try:
            temp_value = jq(".operations[].inputs[] | select (.name | contains (\"Growth Temperature\")).value").transform(biofab_doc)
        except StopIteration:
            print("Warning, could not find temperature for {}".format(original_experiment_id))
            temp_value = None

    # Instead of bottom up from files, process top down from items
    for missing_part_of in missing_part_of_items:
        items = jq(".items[] | select(.part_of==\"" + missing_part_of + "\")").transform(biofab_doc, multiple_output=True)

        if len(items) == 0:
            item = jq(".items[] | select(.item_id==\"" + missing_part_of + "\")").transform(biofab_doc)
            if item is not None:
                items.append(item)

        for item in items:

            time_val = get_timepoint_from_item(item)

            sample_doc = {}

            read_bead_fluorescence_from_item(item, sample_doc)

            item_id = item[item_id_attr]
            try:
                item_source = jq(".items[] | select(.sources[]? == \"" + item_id + "\")").transform(biofab_doc)
            except StopIteration:
                # no source, use the original item
                item_source = item

            if item_source is not None:

                reagents = []

                sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(item_source[item_id_attr], lab, output_doc)
                sample_doc[SampleConstants.LAB_SAMPLE_ID] = namespace_sample_id(item_source[item_id_attr], lab, None)

                if attributes_attr in item_source and (concentration_attr in item_source[attributes_attr] or volume_attr in item_source[attributes_attr]):
                    # reagent
                    media_id = item_source[sample_attr][sample_id_attr]
                    media_name = item_source[sample_attr][sample_name_attr]
                    reagent_obj = None
                    if concentration_attr in item_source[attributes_attr]:
                        reagent_obj = create_media_component(original_experiment_id, media_name, media_id, lab, sbh_query, item_source[attributes_attr][concentration_attr])
                    else:
                        reagent_obj = create_media_component(original_experiment_id, media_name, media_id, lab, sbh_query)

                    if volume_attr in item_source[attributes_attr]:
                        volume_value_unit = create_value_unit(item_source[attributes_attr][volume_attr])
                        reagent_obj["volume"] = volume_value_unit

                    reagents.append(reagent_obj)

                else:
                    # strain
                    add_strain(original_experiment_id, item_source, sample_doc, lab, sbh_query)

                add_inducer_experimental_media(original_experiment_id, item_source, lab, sbh_query, reagents, biofab_doc)

                add_od(item_source, sample_doc)

                add_control(item_source, sample_doc, output_doc)

                add_replicate(item_source, sample_doc)

                if attributes_attr in item_source and media_attr in item_source[attributes_attr]:
                    if sample_id_attr in item_source[attributes_attr][media_attr]:
                        media_id = item_source[attributes_attr][media_attr][sample_id_attr]
                        reagents.append(create_media_component(original_experiment_id, media_id, media_id, lab, sbh_query))
                    else:
                        raise ValueError("No media id? {}".format(item_source))
                else:
                    # check source first
                    if source_attr in item_source:
                        media_source_lookup = jq(".items[] | select(.item_id==\"" + item_source[source_attr][0] + "\")").transform(biofab_doc)
                        if attributes_attr in media_source_lookup and media_attr in media_source_lookup[attributes_attr]:
                            if sample_id_attr in media_source_lookup[attributes_attr][media_attr]:
                                media_id = media_source_lookup[attributes_attr][media_attr][sample_id_attr]
                                reagents.append(create_media_component(original_experiment_id, media_id, media_id, lab, sbh_query))
                            else:
                                raise ValueError("No media id? {}".format(media_source_lookup))
                    else:
                        add_input_media(original_experiment_id, lab, sbh_query, reagents, biofab_doc, item_source)

                if len(reagents) > 0:
                    sample_doc[SampleConstants.CONTENTS] = reagents

            if temp_value is not None:
                sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(str(temp_value) + ":celsius")

            measurement_doc = {}

            if part_of_attr in item_source:
                add_timepoint(time_val, measurement_doc, item_source[part_of_attr], biofab_doc)
            else:
                add_timepoint(time_val, measurement_doc, None, biofab_doc)

            measurement_doc[SampleConstants.FILES] = []

            files = jq(".files[] | select(.sources[]? == \"" + missing_part_of + "\")").transform(biofab_doc, multiple_output=True)

            for file in files:
                add_measurement_type(file, measurement_doc)

                add_measurement_id(measurement_doc, sample_doc, output_doc)

                add_measurement_group_id(measurement_doc, file, sample_doc, output_doc)

                add_file_name(config, file, measurement_doc, original_experiment_id, lab, output_doc)

            add_measurement_doc(measurement_doc, sample_doc, output_doc)
    try:
        validate(output_doc, schema)
        # if verbose:

        #print(json.dumps(output_doc, indent=4))

        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join("output/biofab", os.path.basename(input_file))
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
                convert_biofab(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_biofab(sys.argv[1], sys.argv[2])
