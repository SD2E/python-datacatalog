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


def parse_time(transcriptic_sample_or_file):
    if SampleConstants.TIMEPOINT in transcriptic_sample_or_file:
        time_val = transcriptic_sample_or_file[SampleConstants.TIMEPOINT]
        # 1 hour -> 1:hour
        if time_val.endswith(" hour"):
            time_val = time_val.replace(" hour", ":hour")

        # enum fix
        if time_val.endswith("hours"):
            time_val = time_val.replace("hours", "hour")
        if time_val.endswith("minutes"):
            minute_split = time_val.split(":minutes")
            minute_val = float(minute_split[0])/60.0
            time_val = str(minute_val) + ":hour"
        return time_val
    else:
        return None

"""
Schema closely aligns with V1 target schema
Walk and expand to dictionary/attribute blocks
as necessary
"""
def convert_transcriptic(schema, encoding, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    DEFAULT_BEAD_MODEL = "SpheroTech URCP-38-2K"
    DEFAULT_BEAD_BATCH = "AJ02"
    DEFAULT_CYTOMETER_CHANNELS = ["BL1-A", "FSC-A", "SSC-A"]
    DEFAULT_CYTOMETER_CONFIGURATION = "agave://data-sd2e-community/sample/transcriptic/instruments/flow/attune/1AAS220201014/11232018/cytometer_configuration.json"

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    transcriptic_doc = json.load(open(input_file, encoding=encoding))

    output_doc = {}

    lab = SampleConstants.LAB_TX

    original_experiment_id = transcriptic_doc[SampleConstants.EXPERIMENT_ID]

    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(transcriptic_doc[SampleConstants.EXPERIMENT_ID], lab)

    cp = transcriptic_doc[SampleConstants.CHALLENGE_PROBLEM]
    # TX's name for YG...
    if cp == "YG":
        cp = SampleConstants.CP_YEAST_STATES
    elif cp == "NC":
        cp = SampleConstants.CP_NOVEL_CHASSIS
    else:
        print("Proceeding with CP: {}".format(cp))

    output_doc[SampleConstants.CHALLENGE_PROBLEM] = cp

    output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = transcriptic_doc[SampleConstants.EXPERIMENT_REFERENCE]

    map_experiment_reference(config, output_doc)

    # We need to re-write this reference
    # Strateos uploaded under the former URL and reference name,
    # (“YeastSTATES CRISPR Growth Curves Request”)
    # But the design was run under the latter reference URL and name
    # and the former experiments were adopted into it
    # (YeastSTATES CRISPR Growth Curves Request (422936)“)
    # Fix this by URL
    if output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] == "https://docs.google.com/document/d/1uv_X7CSD5cONEjW7yq4ecI89XQxPQuG5lnmaqshj47o":
        output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = "https://docs.google.com/document/d/1IlR2-ufP_vVfHt15uYocExhyQfEkPnOljYf3Y-rB08g"
        output_doc[SampleConstants.EXPERIMENT_REFERENCE] = "YeastSTATES-CRISPR-Growth-Curves-422936"

    # Group all endogenous promoter experiments together
    if output_doc[SampleConstants.EXPERIMENT_REFERENCE].startswith("NovelChassis-Endogenous-Promoter-"):
        output_doc[SampleConstants.EXPERIMENT_REFERENCE]= "NovelChassis-Endogenous-Promoter"
        output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = "https://docs.google.com/document/d/162OXD2SacWUb4aN1WK7vA2rlKupmcstDpPheAt49ADQ"

    db = mongo.db_connection(config['mongodb'])
    samples_table = db.samples


    output_doc[SampleConstants.LAB] = lab
    output_doc[SampleConstants.SAMPLES] = []
    samples_w_data = 0
    cytometer_channels = DEFAULT_CYTOMETER_CHANNELS
    if SampleConstants.CYTOMETER_CONFIG in transcriptic_doc:
        output_doc[SampleConstants.CYTOMETER_CONFIG] = transcriptic_doc[SampleConstants.CYTOMETER_CONFIG]
        cytometer_channels = []
        for channel in output_doc[SampleConstants.CYTOMETER_CONFIG]['channels']:
            if channel['name'].endswith("-A"):
                cytometer_channels.append(channel['name'])

    inducer_regex = re.compile("\d{1,3}?\.?\d{1,3}?m?n?u?M\s(.*)")

    for transcriptic_sample in transcriptic_doc[SampleConstants.SAMPLES]:
        sample_doc = {}

        # e.g. aq1bsuhh8sb9px/ct1bsmggegqg89
        # first part is a unique sample id
        # second part encodes the measurement operation
        # e.g. grouping for OD or FCS
        tx_sample_measure_id = transcriptic_sample["tx_sample_id"].split("/")
        sample_id = tx_sample_measure_id[0]
        measurement_id = tx_sample_measure_id[1]

        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(sample_id, lab, output_doc)
        sample_doc[SampleConstants.LAB_SAMPLE_ID] = namespace_sample_id(sample_id, lab, None)

        sample_doc[SampleConstants.CONTAINER_ID] = measurement_id

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
                query["sample_id"] = namespace_sample_id(parent_sample_id, lab, output_doc)

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
        parsed_oc = False

        if SampleConstants.CONTENTS in transcriptic_sample:
            # this is sometimes a list, sometimes a single value...
            sample_contents = transcriptic_sample[SampleConstants.CONTENTS]
            if not isinstance(sample_contents, list):
                sample_contents = [sample_contents]

            # Obstacle Course
            # Will contain sub-fields
            # "concentration": "1.0:micromolar",
            # "label": "100mM IPTG",
            # "timepoint": "48:hour"
            for reagent in sample_contents:
                if reagent is None or len(reagent) == 0:
                    print("Warning, reagent value is null or empty string {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
                else:

                    if SampleConstants.LABEL in reagent and len(reagent[SampleConstants.LABEL]) > 0:

                        parsed_oc = True

                        reagent_label = reagent[SampleConstants.LABEL]

                        # Regex split on fluid units
                        # e.g. "100mM IPTG"
                        if reagent_label[0].isdigit() and " " in reagent_label:
                            inducer_match = inducer_regex.match(reagent_label)
                            if not inducer_match:
                                raise ValueError("Could not parse inducer {}".format(reagent_label))
                            reagent_label = inducer_match.group(1)

                        time_concentration_value = None
                        time_concentration_unit = None
                        has_time_unit = False
                        if SampleConstants.TIMEPOINT in reagent:
                            parsed_reagent_time = create_value_unit(reagent[SampleConstants.TIMEPOINT])
                            time_concentration_value = parsed_reagent_time[SampleConstants.VALUE]
                            time_concentration_unit = parsed_reagent_time[SampleConstants.UNIT]
                            has_time_unit = True
                        if SampleConstants.CONCENTRATION in reagent:
                            contents_append_value = create_media_component(original_experiment_id, reagent_label, reagent_label, lab, sbh_query, reagent[SampleConstants.CONCENTRATION])
                        else:
                            contents_append_value = create_media_component(original_experiment_id, reagent_label, reagent_label, lab, sbh_query)
                        if has_time_unit:
                            contents_append_value["timepoint"] = { "value" : time_concentration_value, "unit" : time_concentration_unit }

                        contents.append(contents_append_value)

                    if type(reagent) == str and reagent not in seen_contents:
                        seen_contents.add(reagent)
                        # if we don't have an inducer, and only one reagent, this is that reagent's concenetration
                        if len(sample_contents) == 1 and SampleConstants.CONCENTRATION in transcriptic_sample and "inducer" not in transcriptic_sample:
                            contents.append(create_media_component(original_experiment_id, reagent, reagent, lab, sbh_query, transcriptic_sample[SampleConstants.CONCENTRATION]))
                        else:
                            contents.append(create_media_component(original_experiment_id, reagent, reagent, lab, sbh_query))

        if SampleConstants.MEDIA in transcriptic_sample and SampleConstants.MEDIA_RS_ID in transcriptic_sample:
            media = transcriptic_sample[SampleConstants.MEDIA]
            media_id = transcriptic_sample[SampleConstants.MEDIA_RS_ID]
            if media_id not in seen_contents:
                seen_contents.add(media_id)
                contents.append(create_media_component(original_experiment_id, media, media_id, lab, sbh_query))

        # skip inducer parsing if we parsed via OC array above
        if not parsed_oc and SampleConstants.INDUCER in transcriptic_sample:
            inducer = transcriptic_sample[SampleConstants.INDUCER]
            if inducer != None and len(inducer) > 0:
                if output_doc[SampleConstants.EXPERIMENT_REFERENCE] == "NovelChassis-NAND-Gate":
                    arab_concentration = "25:mM"
                    iptg_concentration = "0.25:mM"
                else:
                    if SampleConstants.CONCENTRATION not in transcriptic_sample:
                        raise ValueError("Inducers without concentration values. TX must provide. Abort! {}".format(inducer))
                    else:
                        arab_concentration = transcriptic_sample[SampleConstants.CONCENTRATION]
                        iptg_concentration = transcriptic_sample[SampleConstants.CONCENTRATION]

                # skip multi-value inducers - handled by contents array above
                if inducer != "None" and len(inducer) > 0 and "," not in inducer:
                    if "+" in inducer:
                        inducer_split = inducer.split("+")
                        if inducer_split[0] not in seen_contents:
                            seen_contents.add(inducer_split[0])
                            if inducer_split[0] == "Arabinose":
                                concentration = arab_concentration
                            elif inducer_split[0] == "IPTG":
                                concentration = iptg_concentration
                            else:
                                raise ValueError("Unknown inducer")
                            contents.append(create_media_component(original_experiment_id, inducer_split[0], inducer_split[0], lab, sbh_query, concentration))
                        if inducer_split[1] not in seen_contents:
                            seen_contents.add(inducer_split[1])
                            if inducer_split[1] == "Arabinose":
                                concentration = arab_concentration
                            elif inducer_split[1] == "IPTG":
                                concentration = iptg_concentration
                            else:
                                raise ValueError("Unknown inducer")
                            contents.append(create_media_component(original_experiment_id, inducer_split[1], inducer_split[1], lab, sbh_query, concentration))
                    else:
                        # Special case for YS. Both means Arabinose and IPTG
                        if inducer == "Both" and output_doc[SampleConstants.CHALLENGE_PROBLEM] == SampleConstants.CP_NOVEL_CHASSIS:
                            inducer = "Arabinose"
                            if inducer not in seen_contents:
                                seen_contents.add(inducer)
                                contents.append(create_media_component(original_experiment_id, inducer, inducer, lab, sbh_query, arab_concentration))

                            inducer = "IPTG"
                            if inducer not in seen_contents:
                                seen_contents.add(inducer)
                                contents.append(create_media_component(original_experiment_id, inducer, inducer, lab, sbh_query, iptg_concentration))
                        elif inducer not in seen_contents:
                            seen_contents.add(inducer)
                            if inducer == "Arabinose":
                                concentration = arab_concentration
                            elif inducer == "IPTG":
                                concentration = iptg_concentration
                            else:
                                if SampleConstants.CONCENTRATION not in transcriptic_sample:
                                    raise ValueError("Unknown inducer or missing concentration value {}".format(inducer))
                                # split on fluid units
                                # e.g. "20uM beta-estradiol"
                                if inducer[0].isdigit() and " " in inducer:
                                    inducer_match = inducer_regex.match(inducer)
                                    if not inducer_match:
                                        raise ValueError("Could not parse inducer {}".format(inducer))
                                    inducer = inducer_match.group(1)
                                concentration = transcriptic_sample[SampleConstants.CONCENTRATION]
                            contents.append(create_media_component(original_experiment_id, inducer, inducer, lab, sbh_query, concentration))

        if len(contents) > 0:
            sample_doc[SampleConstants.CONTENTS] = contents

        #"dna_concentration": "0:nanogram:microliter",
        if "dna_concentration" in transcriptic_sample:
            dna_content = "DNA Reaction Concentration"
            dna_content_concentration = transcriptic_sample["dna_concentration"]
            # clean up inconsistencies
            if dna_content_concentration.endswith("nanogram/microliter"):
                dna_content_concentration = dna_content_concentration.replace("nanogram/microliter", "nanogram:microliter")
            contents.append(create_media_component(original_experiment_id, dna_content, dna_content, lab, sbh_query, dna_content_concentration))

        # strain
        if SampleConstants.STRAIN in transcriptic_sample:
            strain = transcriptic_sample[SampleConstants.STRAIN]

            # local override
            if "Full Name" in transcriptic_sample:
                strain = transcriptic_sample["Full Name"]

            # Normalize TX Sphero Markers
            if strain == "SpheroControl1":
                strain = "SpheroControl"

            if strain == "SpheroControl" and SampleConstants.STANDARD_TYPE not in transcriptic_sample:
                sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_BEAD_FLUORESCENCE

            # Normalize Size Markers
            if strain == "SizeControl":
                strain = "SizeBeadControl"

            # TX does not mark size beads consistently
            if strain == "SizeBeadControl":
                sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_BEAD_SIZE
                # this is a reagent
                sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, strain, strain, lab, sbh_query, strain=False)
            elif strain in ["MediaControl", "MediaControl1", "MediaControl2", "MediaControl3"]:
                sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_MEDIA_BLANK
                # this is a reagent, normalize the value
                sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, "MediaControl", "MediaControl", lab, sbh_query, strain=False)
            else:
                # new TX Live/Dead controls
                if strain == "WT-Dead-Control":
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_CELL_DEATH_POS_CONTROL
                    sample_doc[SampleConstants.CONTROL_CHANNEL] = "RL1-A"
                elif strain == "WT-Live-Control":
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_CELL_DEATH_NEG_CONTROL
                elif strain == "NOR 00 Control":
                    sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                    sample_doc[SampleConstants.CONTROL_CHANNEL] = "BL1-A"
                # ensure strain gets mapped alongside controls
                sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, strain, strain, lab, sbh_query, strain=True)

        #barcode
        if SampleConstants.BARCODE in transcriptic_sample:
            sample_doc[SampleConstants.BARCODE] = transcriptic_sample[SampleConstants.BARCODE]

        #well_label
        if SampleConstants.WELL_LABEL in transcriptic_sample:
            sample_doc[SampleConstants.WELL_LABEL] = transcriptic_sample[SampleConstants.WELL_LABEL]

        # temperature
        temperature_val = transcriptic_sample[SampleConstants.TEMPERATURE]
        # This is a special case for the growth curves experiments.
        temp_prefix = "warm_"
        if temperature_val.startswith(temp_prefix):
            temperature_val = temperature_val[(temperature_val.index(temp_prefix) + len(temp_prefix)):]
            sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(temperature_val + ":celsius")
        else:
            sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(temperature_val)

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
        time_val = parse_time(transcriptic_sample)

        # controls and standards
        # map standard for, type,
        if SampleConstants.STANDARD_TYPE in transcriptic_sample:
            tx_standard_type = transcriptic_sample[SampleConstants.STANDARD_TYPE]
            if tx_standard_type not in [""]:
                # CONTROL samples are media controls (blanks)
                if tx_standard_type == "CONTROL":
                    tx_standard_type = "MEDIA_BLANK"
                elif tx_standard_type == "SIZE_BEAD_FLUORESCENCE":
                    # TX calls this something slightly different
                    tx_standard_type = "BEAD_SIZE"

                sample_doc[SampleConstants.STANDARD_TYPE] = tx_standard_type
        if SampleConstants.STANDARD_FOR in transcriptic_sample:
            standard_for = transcriptic_sample[SampleConstants.STANDARD_FOR]
            if len(standard_for) > 0:
                sample_doc[SampleConstants.STANDARD_FOR] = standard_for

        # map control for, type
        if SampleConstants.CONTROL_TYPE in transcriptic_sample:
            ct = transcriptic_sample[SampleConstants.CONTROL_TYPE]
            # not a valid control type
            # this is parsed by sample id, below
            if ct not in ["SYTOX_LIVE_DEAD", ""]:
                sample_doc[SampleConstants.CONTROL_TYPE] = ct
        if SampleConstants.CONTROL_FOR in transcriptic_sample:
            control_for = transcriptic_sample[SampleConstants.CONTROL_FOR]
            if len(control_for) > 0:
                sample_doc[SampleConstants.CONTROL_FOR] = control_for

        # fill in attributes if we have a bead standard
        if SampleConstants.STANDARD_TYPE in sample_doc and \
            sample_doc[SampleConstants.STANDARD_TYPE] == SampleConstants.STANDARD_BEAD_FLUORESCENCE and \
                SampleConstants.STANDARD_ATTRIBUTES not in sample_doc:
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES] = {}
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_MODEL] = DEFAULT_BEAD_MODEL
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_BATCH] = DEFAULT_BEAD_BATCH

        # Fill in Strain for Media_Blank if it does not exist
        if SampleConstants.STANDARD_TYPE in sample_doc and \
            sample_doc[SampleConstants.STANDARD_TYPE] == SampleConstants.STANDARD_MEDIA_BLANK and \
                SampleConstants.STRAIN not in sample_doc:
            sample_doc[SampleConstants.STRAIN] = create_mapped_name(original_experiment_id, "MediaControl", "MediaControl", lab, sbh_query, strain=False)

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

            # try to parse the file directly
            file_time_val = parse_time(file)
            if file_time_val is not None:
                time_val = file_time_val

            if time_val is not None:
                measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time_val)

            measurement_doc[SampleConstants.FILES] = []

            measurement_type = file[SampleConstants.M_TYPE]

            file_name = file[SampleConstants.M_NAME]
            # same logic as uploads manager
            file_name = safen_filename(file_name)

            # infer for r1brvabq9fjgd_r1bry2xb8scz4_seq_samples
            if measurement_type == "UNKNOWN" and file_name.endswith(".fastq.gz"):
                measurement_type = SampleConstants.MT_RNA_SEQ

            # enum fix
            if measurement_type == "RNASeq":
                measurement_type = SampleConstants.MT_RNA_SEQ

            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type

            # apply defaults, if nothing mapped
            if measurement_type == SampleConstants.MT_FLOW:
                if SampleConstants.M_CHANNELS not in measurement_doc:
                    measurement_doc[SampleConstants.M_CHANNELS] = cytometer_channels

                if SampleConstants.CYTOMETER_CONFIG not in output_doc and SampleConstants.M_INSTRUMENT_CONFIGURATION not in measurement_doc:
                    measurement_doc[SampleConstants.M_INSTRUMENT_CONFIGURATION] = DEFAULT_CYTOMETER_CONFIGURATION

            # TX can repeat measurement ids
            # across multiple measurement types, append
            # the type so we have a distinct id per actual grouped measurement
            typed_measurement_id = '.'.join([measurement_id, measurement_type])

            # generate a measurement id unique to this sample
            measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(str(measurement_counter), output_doc[SampleConstants.LAB], sample_doc, output_doc)

            # record a measurement grouping id to find other linked samples and files
            measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(typed_measurement_id, output_doc[SampleConstants.LAB], sample_doc, output_doc)

            if file_name in seen_files_per_sample:
                print("Warning, duplicate filename, skipping, {}".format(file_name))
                continue
            else:
                seen_files_per_sample.add(file_name)

            file_type = SampleConstants.infer_file_type(file_name)
            file_name_final = file_name

            # normalize when TX sends non-relative paths
            # s3://sd2e-community/uploads/transcriptic/2019/11/YeastSTATES-CRISPR-Growth-Curves/r1ds8b4tdyuqxb/od_1.csv -> od_1.csv
            # transcriptic/201911/YeastSTATES-CRISPR-Growth-Curves-with-Plate-Reader-Optimization/r1dtbufcpd2ktr/od_1.csv -> od_1.csv

            if file_name.startswith('s3') or file_name.count("/") >= 2:
                file_name_final = file_name.split(original_experiment_id)[-1]

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

        # Handle missing measurements
        if "dropout_type" in transcriptic_sample:
            dt = transcriptic_sample["dropout_type"]

            missing_measurement_doc = {}

            if time_val is not None:
                missing_measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time_val)

            missing_measurement_doc[SampleConstants.MEASUREMENT_TYPE] = dt
            if dt == SampleConstants.MT_FLOW:
                missing_ft = SampleConstants.F_TYPE_FCS
            elif dt == SampleConstants.MT_PLATE_READER:
                missing_ft = SampleConstants.F_TYPE_CSV
            elif dt == SampleConstants.MT_DNA_SEQ:
                missing_ft = SampleConstants.F_TYPE_FASTQ
            elif dt == SampleConstants.MT_RNA_SEQ:
                missing_ft = SampleConstants.F_TYPE_FASTQ
            else:
                raise ValueError("Cannot determine file for missing measurement type {}".format(dt))

            missing_measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id("missing_" + dt, output_doc[SampleConstants.LAB], sample_doc, output_doc)
            missing_measurement_doc[SampleConstants.FILES] = [{SampleConstants.M_TYPE : missing_ft, SampleConstants.M_NAME : namespace_file_id("missing_file", output_doc[SampleConstants.LAB], missing_measurement_doc, output_doc)}]
            sample_doc[SampleConstants.MISSING_MEASUREMENTS] = [missing_measurement_doc]

        if SampleConstants.MEASUREMENTS not in sample_doc:
            sample_doc[SampleConstants.MEASUREMENTS] = []
        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    print('Samples in file: {}'.format(len(transcriptic_doc)))
    print('Samples with data: {}'.format(samples_w_data))

    try:
        validate(output_doc, schema)
        # if verbose:
        # print(json.dumps(output_doc, indent=4))
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
