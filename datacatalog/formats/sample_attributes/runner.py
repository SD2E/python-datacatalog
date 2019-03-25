#!/usr/bin/python
import json
import sys
import os
import six
import re

from jsonschema import validate, ValidationError
from sbol import *
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *

from ...agavehelpers import AgaveHelper
from ..common import SampleConstants
from ..common import namespace_file_id, namespace_sample_id, namespace_measurement_id, namespace_lab_id, create_media_component, create_mapped_name, create_value_unit, map_experiment_reference, namespace_experiment_id
from jq import jq
import requests

attributes_attr = "attributes"
files_attr = "files"
od600_attr = "od600"

DEFAULT_BEAD_MODEL = "SpheroTech URCP-38-2K"
DEFAULT_BEAD_BATCH = "AJ02"
DEFAULT_CYTOMETER_CHANNELS = ["FSC-A", "SSC-A", "BL1-A"]
DEFAULT_CYTOMETER_CONFIGURATION = "agave://data-sd2e-community/sample/transcriptic/instruments/flow/attune/1AAS220201014/11232018/cytometer_configuration.json"
TX_API_URL_BASE = "https://secure.transcriptic.com/api/runs/"

# Assumption: keys from different dicts don't overlap
# If they do overlap, replace the second last line with commented code for a true merge
def merge_dicts(dicts):
    super_dict = {}
    for d in dicts:
        for k, v in d.items():
            l=super_dict.setdefault(k,v)
            #l=super_dict.setdefault(k,[])
            #if v not in l:
            #    l.append(v)
    return super_dict

def get_tx_data(eid, email, token):
    #print("eid: {} email: {} token: {}".format(eid, email, token))
    response = requests.get(TX_API_URL_BASE + eid, headers={'X-User-Email': email, 'X-User-Token': token, 'Accept': 'application/json'})
    print("TX API Response Code {}".format(response.status_code))
    response_json = json.loads(response.text)
    request_json = json.loads(response_json['data']['attributes']['request'])
    for elem in request_json['raw']['instructions']:
        if 'where' in elem:
            return elem
            
    return None
    
def convert_sample_attributes(schema, encoding, input_file, email, token, verbose=True, output=True, output_file=None, config={}, enforce_validation=True, reactor=None):

    if reactor is not None:
        helper = AgaveHelper(reactor.client)
        print("Helper loaded")
    else:
        print("Helper not loaded")

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(config["sbh"]["user"], config["sbh"]["password"])

    sample_attributes_doc = json.load(open(input_file, encoding=encoding))

    output_doc = {}

    output_doc[SampleConstants.SAMPLES] = []

    lab = None
    experiment_id = None

    exp_id_re = re.compile("agave:\/\/.*\/(.*)\/\d\/instrument_output")
    eid = None
    tx_data = None

    for sample_attributes_sample in sample_attributes_doc:
        #print("sample_attributes_sample: {}".format(sample_attributes_sample))
        sample_doc = {}
        sample_doc[SampleConstants.MEASUREMENTS] = []
        
        # try to figure out the lab, experiment_id, cp, etc from the filename
        attr_matches = [attr for attr in sample_attributes_sample if attr.endswith(attributes_attr)]
        attr_sample_content = []
        for attr_match in attr_matches:
            attr_sample_content.append(sample_attributes_sample[attr_match])
        attr_sample_content = merge_dicts(attr_sample_content)
        #print("attr_sample_content: {}".format(attr_sample_content))

        measurement_group_ids = {}
        measurement_group_ids[SampleConstants.MT_PLATE_READER] = measurement_group_ids[SampleConstants.MT_FLOW] = None
        if "operators" in sample_attributes_sample:
            #print("found operators")
            for operator in sample_attributes_sample["operators"]:
                #print("operator: {}".format(operator))
                if "parameters" in operator["operator"]:
                    #print("found parameters: {}".format(operator["operator"]["parameters"]))
                    parameters = operator["operator"]["parameters"]
                    if parameters is not None:
                        for parameter in parameters:
                            if SampleConstants.TEMPERATURE in parameter:
                                temperature = parameter[SampleConstants.TEMPERATURE]
                                temperature = temperature.replace("centrigrade", "celsius")
                                sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(temperature)
                if "type" in operator["operator"] and "id" in operator["operator"]:
                    type = operator["operator"]["type"];
                    id = operator["operator"]["id"];
                    if type == "spectrophotometry":
                        measurement_group_ids[SampleConstants.MT_PLATE_READER] = id
                    elif type == "flow_cytometry":
                        measurement_group_ids[SampleConstants.MT_FLOW] = id

        if len(attr_matches)>0 and files_attr in attr_sample_content:
            # determinstically derive measurement ids from sample_id + counter (local to sample)
            measurement_counter = 1
            if attr_sample_content[files_attr] is None:
                print("**** files field is None, skipping sample: {}".format(attr_sample_content))
                continue

            for file in attr_sample_content[files_attr]:
                
                exp_match = exp_id_re.match(file)
                if eid is None:
                    eid = exp_match.group(1)
                relative_file_path = file[(re.search(eid,file).start()+len(eid)+1):]
                if lab is None: 
                    # lab mapping
                    if "transcriptic" in file and SampleConstants.LAB not in output_doc:
                        lab = SampleConstants.LAB_TX
                        output_doc[SampleConstants.LAB] = lab
                    
                    # CP mapping
                    if "yeast-gates" in file and SampleConstants.CHALLENGE_PROBLEM not in output_doc:
                        # provide this manually
                        output_doc[SampleConstants.EXPERIMENT_REFERENCE] = "Yeast-Gates"

                    # Tricky. Parse experiment id out of the below (r1bbktv6x4xke)
                    # agave://data-sd2e-community/transcriptic/yeast-gates_q0/r1bbktv6x4xke/3/instrument_output/s877_R31509.fcs ?                
                    if exp_match and SampleConstants.EXPERIMENT_ID not in output_doc:
                        experiment_id = namespace_experiment_id(eid, lab)
                        output_doc[SampleConstants.EXPERIMENT_ID] = experiment_id
                        #print("experiment_id: {}".format(experiment_id))
    
                    map_experiment_reference(config, output_doc)
                
                measurement_doc = {}
                # timepoint
                if tx_data is None:
                    tx_data = get_tx_data(eid, email, token)
                timepoint = tx_data['duration']
                measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(timepoint)

                measurement_doc[SampleConstants.FILES] = []
                
                #print("file: {}".format(file))
                if (file.endswith("fcs")):
                    measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_FLOW
                elif (file.endswith("csv")):
                    measurement_doc[SampleConstants.MEASUREMENT_TYPE] = SampleConstants.MT_PLATE_READER
                    
                sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(str(sample_attributes_sample["sample"]), lab, output_doc)
                #print("sample_id: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))

                # generate a measurement id unique to this sample
                measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(str(measurement_counter), output_doc[SampleConstants.LAB], sample_doc, output_doc)
                # record a measurement grouping id to find other linked samples and files
                group_id = measurement_group_ids[measurement_doc[SampleConstants.MEASUREMENT_TYPE]]
                if group_id == None:
                    group_id = ".".join([str(eid), measurement_doc[SampleConstants.MEASUREMENT_TYPE].lower()])
                else:
                    group_id = ".".join([str(eid), str(group_id)])
                measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(group_id, output_doc[SampleConstants.LAB], sample_doc, output_doc)

                file_name = file
                file_type = SampleConstants.infer_file_type(file_name)
                file_name_final = relative_file_path
                measurement_doc[SampleConstants.FILES].append(
                    {SampleConstants.M_NAME: file_name_final,
                     SampleConstants.M_TYPE: file_type,
                     SampleConstants.M_LAB_LABEL: [SampleConstants.M_LAB_LABEL_RAW],
                     SampleConstants.FILE_ID: namespace_file_id("1", output_doc[SampleConstants.LAB], measurement_doc, output_doc),
                     SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0})

                # apply defaults, if nothing mapped
                if measurement_doc[SampleConstants.MEASUREMENT_TYPE] == SampleConstants.MT_FLOW:
                    if SampleConstants.M_CHANNELS not in measurement_doc:
                        measurement_doc[SampleConstants.M_CHANNELS] = DEFAULT_CYTOMETER_CHANNELS
                    if SampleConstants.M_INSTRUMENT_CONFIGURATION not in measurement_doc:
                        measurement_doc[SampleConstants.M_INSTRUMENT_CONFIGURATION] = DEFAULT_CYTOMETER_CONFIGURATION                

                sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)

                measurement_counter = measurement_counter + 1

        if lab is None:
            raise ValueError("Could not parse lab from sample {}".format(sample_attributes_sample))

        contents = []
        if SampleConstants.MEDIA in attr_sample_content:
            reagent = attr_sample_content[SampleConstants.MEDIA]
            contents.append(create_media_component(experiment_id, reagent, reagent, lab, sbh_query))

        # strain
        if SampleConstants.STRAIN in attr_sample_content:
            strain = attr_sample_content[SampleConstants.STRAIN]
            sample_doc[SampleConstants.STRAIN] = create_mapped_name(experiment_id, strain, strain, lab, sbh_query, strain=True)

        # fill in attributes if we have a bead standard
        if "bead_colony" in attr_sample_content and "beads_spherotech_rainbow" in attr_sample_content["bead_colony"] and \
            SampleConstants.STANDARD_ATTRIBUTES not in sample_doc: 
            sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_BEAD_FLUORESCENCE
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES] = {}
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_MODEL] = DEFAULT_BEAD_MODEL
            sample_doc[SampleConstants.STANDARD_ATTRIBUTES][SampleConstants.BEAD_BATCH] = DEFAULT_BEAD_BATCH

        if SampleConstants.CONTROL_TYPE not in sample_doc and SampleConstants.STRAIN in sample_doc:
            #print("strain: {}".format(sample_doc[SampleConstants.STRAIN]))
            if "UWBIOFAB_22544" in sample_doc[SampleConstants.STRAIN][SampleConstants.SBH_URI]:
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_EMPTY_VECTOR
            elif "UWBF_6390" in sample_doc[SampleConstants.STRAIN][SampleConstants.SBH_URI]:
                sample_doc[SampleConstants.CONTROL_TYPE] = SampleConstants.CONTROL_HIGH_FITC
                sample_doc[SampleConstants.CONTROL_CHANNEL] = "BL1-A"

        # replicate
        if SampleConstants.REPLICATE in attr_sample_content:
            replicate_val = attr_sample_content[SampleConstants.REPLICATE]
            sample_doc[SampleConstants.REPLICATE] = replicate_val

        # od
        if "od" in attr_sample_content:
            od_val = attr_sample_content["od"]
            sample_doc[SampleConstants.INOCULATION_DENSITY] = create_value_unit(str(od_val) + ":" + od600_attr)
        
        # make sure temperature is populated
        if SampleConstants.TEMPERATURE not in sample_doc:
            if eid is None:
                eid = experiment_id.rsplit('.', 1)[-1]
            if tx_data is None:
                tx_data = get_tx_data(eid, email, token)
            if "warm_30" in tx_data['where']:
                temperature = "30.0:celsius"
            elif "warm_37" in tx_data['where']:
                temperature = "37.0:celsius"
            sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(temperature)
        
        if len(contents) > 0:
            sample_doc[SampleConstants.CONTENTS] = contents

        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    try:
        validate(output_doc, schema)
        # if verbose:
        #print(json.dumps(output_doc, indent=4))
        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join("output/sample_attributes", os.path.basename(input_file))
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
    tx_credential = json.load(open("tx_credential.json"))
    email = tx_credential['EMAIL']
    token = tx_credential['TOKEN']
    if os.path.isdir(path):
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            print(file_path)
            if file_path.endswith(".js") or file_path.endswith(".json"):
                convert_sample_attributes(sys.argv[1], file_path, email, token)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_sample_attributes(sys.argv[1], sys.argv[2], email, token)
