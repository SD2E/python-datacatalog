#!/usr/bin/python
import json
import sys
import os
import six
import pymongo

from jsonschema import validate
from jsonschema import ValidationError
# Hack hack
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common import SampleConstants
from common import namespace_sample_id, namespace_file_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *
from sbol import *
from datacatalog.agavehelpers import AgaveHelper

"""
Schema closely aligns with V1 target schema
Walk and expand to dictionary/attribute blocks
as necessary
"""


def convert_transcriptic(schema_file, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    DEFAULT_BEAD_MODEL = "SpheroTech URCP-38-2K"
    DEFAULT_BEAD_BATCH = "AJ02"
    DEFAULT_CYTOMETER_CHANNELS = ["BL1-A", "FSC-A", "SSC-A", "RL1-A"]
    DEFAULT_CYTOMETER_CONFIGURATION = "agave://data-sd2e-community/sample/transcriptic/instruments/flow/attune/1AAS220201014/11232018/cytometer_configuration.json"

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)

    schema = json.load(open(schema_file))
    transcriptic_doc = json.load(open(input_file, encoding=encoding))

    output_doc = {}

    lab = SampleConstants.LAB_TX

    original_experiment_id = transcriptic_doc[SampleConstants.EXPERIMENT_ID]

    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(transcriptic_doc[SampleConstants.EXPERIMENT_ID], lab)

    cp = transcriptic_doc[SampleConstants.CHALLENGE_PROBLEM]
    # TX's name for YG...
    if cp == "YG":
        cp = SampleConstants.CP_YEAST_GATES
    elif cp == "NC":
        cp = SampleConstants.CP_NOVEL_CHASSIS
    else:
        raise ValueError("Unknown TX CP: {}".format(cp))

    output_doc[SampleConstants.CHALLENGE_PROBLEM] = cp

    output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = transcriptic_doc[SampleConstants.EXPERIMENT_REFERENCE]

    map_experiment_reference(config, output_doc)

    db_uri = config['cp_db_uri']
    client = pymongo.MongoClient(db_uri)
    db = client[config['samples_db']]
    samples_table = db.samples

    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []
    samples_w_data = 0

    for transcriptic_sample in transcriptic_doc[SampleConstants.SAMPLES]:
        sample_doc = {}

        # e.g. aq1bsuhh8sb9px/ct1bsmggegqg89
        # first part is a unique sample id
        # second part encodes the measurement operation
        # e.g. grouping for OD or FCS
        tx_sample_measure_id = transcriptic_sample["tx_sample_id"].split("/")
        sample_id = tx_sample_measure_id[0]
        measurement_id = tx_sample_measure_id[1]

        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(sample_id, lab)

        # parse inducer, strain, and replicate from parents, if available
        if "parents" in transcriptic_sample:
            parents = transcriptic_sample["parents"]

            parent_replicates = set()
            parent_strains = set()
            parent_contents = set()

            for parent in parents:
                parent_sample_id_split = parent.split("/")
                parent_sample_id = parent_sample_id_split[0]
                query = {}
                query["sample_id"] = namespace_sample_id(parent_sample_id, lab)

                matches = list(samples_table.find(query).limit(1))
                if len(matches) == 0:
                    raise ValueError("Error: Could not find parent: {}".format(query["sample_id"]))

                for match in matches:
                    if "replicate" in match:
                        parent_replicates.add(match["replicate"])
                    if "strain" in match:
                        parent_strains.add(match["strain"]["lab_id"].split(".")[-1])
                    if "contents" in match:
                        for content in match["contents"]:
                            if content != "None":
                                parent_contents.add(content["name"]["lab_id"].split(".")[-1])

            if len(parent_replicates) != 1:
                raise ValueError("Zero or more than one parent replicate? {} {}".format(parents, parent_replicates))
            if len(parent_strains) != 1:
                raise ValueError("Zero or more than one parent strain? {} {}".format(parents, parent_strains))

            if SampleConstants.REPLICATE not in transcriptic_sample or transcriptic_sample[SampleConstants.REPLICATE] == None:
                transcriptic_sample[SampleConstants.REPLICATE] = list(parent_replicates)[0]
            if SampleConstants.STRAIN not in transcriptic_sample:
                transcriptic_sample[SampleConstants.STRAIN] = list(parent_strains)[0]
            if SampleConstants.CONTENTS not in transcriptic_sample:
                transcriptic_sample[SampleConstants.CONTENTS] = list(parent_contents)

        # media
        contents = []
        # parent can override child values, track these
        seen_contents = set()
        if SampleConstants.CONTENTS in transcriptic_sample:
            # this is sometimes a list, sometimes a single value...
            sample_contents = transcriptic_sample[SampleConstants.CONTENTS]
            if not isinstance(sample_contents, list):
                sample_contents = [sample_contents]

            for reagent in sample_contents:
                if reagent is None or len(reagent) == 0:
                    print("Warning, reagent value is null or empty string {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
                else:
                    if reagent not in seen_contents:
                        seen_contents.add(reagent)
                        if len(sample_contents) == 1 and SampleConstants.CONCENTRATION in transcriptic_sample:
                            contents.append(create_media_component(original_experiment_id, reagent, reagent, lab, sbh_query, transcriptic_sample[SampleConstants.CONCENTRATION]))
                        else:
                            contents.append(create_media_component(original_experiment_id, reagent, reagent, lab, sbh_query))

        if SampleConstants.MEDIA in transcriptic_sample and SampleConstants.MEDIA_RS_ID in transcriptic_sample:
            media = transcriptic_sample[SampleConstants.MEDIA]
            media_id = transcriptic_sample[SampleConstants.MEDIA_RS_ID]
            if media_id not in seen_contents:
                seen_contents.add(media_id)
                contents.append(create_media_component(original_experiment_id, media, media_id, lab, sbh_query))

        if SampleConstants.INDUCER in transcriptic_sample:
            inducer = transcriptic_sample[SampleConstants.INDUCER]
            #"Arabinose+IPTG"
            if inducer != "None":
                if "+" in inducer:
                    inducer_split = inducer.split("+")
                    if inducer_split[0] not in seen_contents:
                        seen_contents.add(inducer_split[0])
                        contents.append(create_media_component(original_experiment_id, inducer_split[0], inducer_split[0], lab, sbh_query))
                    if inducer_split[1] not in seen_contents:
                        seen_contents.add(inducer_split[1])
                        contents.append(create_media_component(original_experiment_id, inducer_split[1], inducer_split[1], lab, sbh_query))
                else:
                    if inducer not in seen_contents:
                        seen_contents.add(inducer)
                        contents.append(create_media_component(original_experiment_id, inducer, inducer, lab, sbh_query))

        if len(contents) > 0:
            sample_doc[SampleConstants.CONTENTS] = contents

        # strain
        if SampleConstants.STRAIN in transcriptic_sample:
            strain = transcriptic_sample[SampleConstants.STRAIN]

            # TX does not mark size beads consistently
            if strain == "SizeBeadControl":
                sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_BEAD_SIZE
                # this is a reagent
                sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, strain, strain, lab, sbh_query, strain=False)
            else:
                sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, strain, strain, lab, sbh_query, strain=True)

        # temperature
        sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(transcriptic_sample[SampleConstants.TEMPERATURE])

        # od
        if SampleConstants.INOCULATION_DENSITY in transcriptic_sample:
            sample_doc[SampleConstants.INOCULATION_DENSITY] = create_value_unit(transcriptic_sample[SampleConstants.INOCULATION_DENSITY])

        # replicate
        replicate_val = transcriptic_sample[SampleConstants.REPLICATE]
        if replicate_val is None:
            print("Warning, replicate value is null, sample {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
        else:
            if isinstance(replicate_val, six.string_types):
                replicate_val = int(replicate_val)
            sample_doc[SampleConstants.REPLICATE] = replicate_val

        # time
        time_val = None
        if SampleConstants.TIMEPOINT in transcriptic_sample:
            time_val = transcriptic_sample[SampleConstants.TIMEPOINT]
            # enum fix
            if time_val.endswith("hours"):
                time_val = time_val.replace("hours", "hour")
            if time_val.endswith("minutes"):
                minute_split = time_val.split(":minutes")
                minute_val = float(minute_split[0])/60.0
                time_val = str(minute_val) + ":hour"

        # controls and standards
        # map standard for, type,
        if SampleConstants.STANDARD_TYPE in transcriptic_sample:
            sample_doc[SampleConstants.STANDARD_TYPE] = transcriptic_sample[SampleConstants.STANDARD_TYPE]
        if SampleConstants.STANDARD_FOR in transcriptic_sample:
            standard_for = transcriptic_sample[SampleConstants.STANDARD_FOR]
            if len(standard_for) != 0 or sample_doc[SampleConstants.STANDARD_TYPE] != SampleConstants.STANDARD_MEDIA_BLANK:
                sample_doc[SampleConstants.STANDARD_FOR] = standard_for

        # map control for, type
        if SampleConstants.CONTROL_TYPE in transcriptic_sample:
            sample_doc[SampleConstants.CONTROL_TYPE] = transcriptic_sample[SampleConstants.CONTROL_TYPE]
        if SampleConstants.CONTROL_FOR in transcriptic_sample:
            sample_doc[SampleConstants.CONTROL_FOR] = transcriptic_sample[SampleConstants.CONTROL_FOR]

        # fill in attributes if we have a bead standard
        if SampleConstants.STANDARD_TYPE in sample_doc and \
            sample_doc[SampleConstants.STANDARD_TYPE] == SampleConstants.STANDARD_BEAD_FLUORESCENCE and \
                SampleConstants.STANDARD_ATTRIBUTES not in sample_doc:
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES] = {}
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_MODEL] = DEFAULT_BEAD_MODEL
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_BATCH] = DEFAULT_BEAD_BATCH

        # if control types are not available, infer based on sample ids
        # this is brittle, but the best we can do right now with the output provided
        # "wt-control-1" = precursor to "WT-Dead-Control" or "WT-Live-Control"
        # "NOR 00 Control" = "HIGH_FITC"
        # "WT-Dead-Control" = "CELL_DEATH_POS_CONTROL" - positive for the sytox stain
        # "WT-Live-Control" = "CELL_DEATH_NEG_CONTROL" - negative for the sytox stain
        # we also need to indicate the control channels the fluorescence controls
        # this is not known by the lab typically, has to be provided externally
        original_sample_id = tx_sample_measure_id = transcriptic_sample[SampleConstants.SAMPLE_ID]
        if SampleConstants.CONTROL_TYPE not in transcriptic_sample:
            if original_sample_id == "wt-control-1":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
            elif original_sample_id == "NOR 00 Control":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                sample_doc[SampleConstants.CONTROL_CHANNEL] = "BL1-A"
            elif original_sample_id == "WT-Dead-Control":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_CELL_DEATH_POS_CONTROL
                sample_doc[SampleConstants.CONTROL_CHANNEL] = "RL1-A"
            elif original_sample_id == "WT-Live-Control":
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_CELL_DEATH_NEG_CONTROL

        # Novel Chassis Positive and Negative Controls
        # TODO: Refactor into common function, vs. lab specific?
        # NC does not provide control mappings
        # Use the default NC negative strain, if CP matches
        # Match on lab ID for now, as this is unambiguous given dictionary common name changes
        # do the same thing for positive control
        if SampleConstants.CONTROL_TYPE not in sample_doc and \
            SampleConstants.STRAIN in sample_doc and \
                output_doc[SampleConstants.CHALLENGE_PROBLEM] == SampleConstants.CP_NOVEL_CHASSIS:
            if sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("MG1655_WT", output_doc[SampleConstants.LAB]):
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
            elif sample_doc[SampleConstants.STRAIN][SampleConstants.LAB_ID] == namespace_lab_id("MG1655_pJS007_LALT__I1__IcaRA", output_doc[SampleConstants.LAB]):
                # ON without IPTG, OFF with IPTG, plasmid (high level)
                # we also need to indicate the control channels for the fluorescence control
                # this is not known by the lab typically, has to be provided externally
                if SampleConstants.CONTENTS not in sample_doc:
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                    sample_doc[SampleConstants.CONTROL_CHANNEL] = "BL1-A"
                else:
                    found = False
                    for content in sample_doc[SampleConstants.CONTENTS]:
                        if SampleConstants.NAME in content and SampleConstants.LABEL in content[SampleConstants.NAME]:
                            content_label = content[SampleConstants.NAME][SampleConstants.LABEL]
                            if content_label == "IPTG":
                                found = True
                    if not found:
                        sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                        sample_doc[SampleConstants.CONTROL_CHANNEL] = "BL1-A"


        # determinstically derive measurement ids from sample_id + counter (local to sample)
        measurement_counter = 1

        # TX sending duplicate files
        seen_files_per_sample = set()

        for file in transcriptic_sample[SampleConstants.FILES]:
            measurement_doc = {}

            if time_val is not None:
                measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time_val)

            measurement_doc[SampleConstants.FILES] = []

            measurement_type = file[SampleConstants.M_TYPE]

            # enum fix
            if measurement_type == "RNASeq":
                measurement_type = SampleConstants.MT_RNA_SEQ

            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type

            # apply defaults, if nothing mapped
            if measurement_type == SampleConstants.MT_FLOW:
                if SampleConstants.M_CHANNELS not in measurement_doc:
                    measurement_doc[SampleConstants.M_CHANNELS] = DEFAULT_CYTOMETER_CHANNELS
                if SampleConstants.M_INSTRUMENT_CONFIGURATION not in measurement_doc:
                    measurement_doc[SampleConstants.M_INSTRUMENT_CONFIGURATION] = DEFAULT_CYTOMETER_CONFIGURATION

            # TX can repeat measurement ids
            # across multiple measurement types, append
            # the type so we have a distinct id per actual grouped measurement
            typed_measurement_id = '.'.join([measurement_id, measurement_type])

            # generate a measurement id unique to this sample
            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(".".join([sample_doc[SampleConstants.SAMPLE_ID], str(measurement_counter)]), output_doc[SampleConstants.LAB])

            # record a measurement grouping id to find other linked samples and files
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(typed_measurement_id, output_doc[SampleConstants.LAB])

            measurement_counter = measurement_counter + 1

            file_name = file[SampleConstants.M_NAME]

            if file_name in seen_files_per_sample:
                print("Warning, duplicate filename, skipping, {}".format(file_name))
                continue
            else:
                seen_files_per_sample.add(file_name)

            file_type = SampleConstants.infer_file_type(file_name)
            file_name_final = file_name
            if file_name.startswith('s3'):
                file_name_final = file_name.split(original_experiment_id)[-1]
                if file_name_final.startswith("/"):
                    file_name_final = file_name_final[1:]

            measurement_doc[SampleConstants.FILES].append(
                {SampleConstants.M_NAME: file_name_final,
                 SampleConstants.M_TYPE: file_type,
                 SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
                 SampleConstants.FILE_ID: namespace_file_id(".".join([sample_doc[SampleConstants.SAMPLE_ID], str(measurement_counter)]), output_doc[SampleConstants.LAB]),
                 SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})

            if SampleConstants.MEASUREMENTS not in sample_doc:
                sample_doc[SampleConstants.MEASUREMENTS] = []
            sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)
            samples_w_data = samples_w_data + 1
            #print('sample {} / measurement {} contains {} files'.format(sample_doc[SampleConstants.SAMPLE_ID], file_name, len(measurement_doc[SampleConstants.FILES])))

        if SampleConstants.MEASUREMENTS not in sample_doc:
            sample_doc[SampleConstants.MEASUREMENTS] = []
        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    print('Samples in file: {}'.format(len(transcriptic_doc)))
    print('Samples with data: {}'.format(samples_w_data))

    try:
        validate(output_doc, schema)
        # if verbose:
        #print(json.dumps(output_doc, indent=4))
        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join(
                    "output/transcriptic", os.path.basename(input_file))
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
                convert_transcriptic(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_transcriptic(sys.argv[1], sys.argv[2])
