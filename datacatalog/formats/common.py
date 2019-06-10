
from synbiohub_adapter.SynBioHubUtil import SD2Constants
import pymongo
import datacatalog
from ..filetypes import infer_filetype
from datacatalog.utils import safen_path

"""Some constants to populate samples-schema.json
   compliant outputs
"""
class SampleConstants():

    """Obvious issues with this, welcome something more robust.
    """
    def infer_file_type(file_name):
        file_name = file_name.lower()
        return infer_filetype(file_name, check_exists=False, permissive=True).label

    # For circuits
    LOGIC_PREFIX = "http://www.openmath.org/cd/logic1#"

    # experiment
    EXPERIMENT_ID = "experiment_id"
    CHALLENGE_PROBLEM = "challenge_problem"

    CP_NOVEL_CHASSIS = "NOVEL_CHASSIS"

    CP_YEAST_STATES = "YEAST_STATES"

    EXPERIMENT_REFERENCE = "experiment_reference"
    EXPERIMENT_REFERENCE_URL = "experiment_reference_url"
    # EXPT_DEFAULT_REFERENCE_GINKGO = "NovelChassis-NAND-Gate"

    LAB = "lab"
    LAB_GINKGO = "Ginkgo"
    LAB_TX = "Transcriptic"
    LAB_UWBF = "UW_BIOFAB"
    LAB_CALTECH = "Caltech"
    LAB_MARSHALL = "Marshall"

    # samples
    SAMPLES = "samples"
    SAMPLE_ID = "sample_id"
    LAB_SAMPLE_ID = "lab_sample_id"
    REFERENCE_SAMPLE_ID = "reference_sample_id"
    STRAIN = "strain"
    STRAIN_CONCENTRATION = "strain_concentration"
    REAGENT_CONCENTRATION = "reagent_concentration"
    GENETIC_CONSTRUCT = "genetic_construct"
    CONTENTS = "contents"
    INDUCER = "inducer"
    MEDIA = "media"
    CONCENTRATION = "concentration"
    MEDIA_RS_ID = "media_rs_id"
    REPLICATE = "replicate"
    INOCULATION_DENSITY = "inoculation_density"
    TEMPERATURE = "temperature"
    TIMEPOINT = "timepoint"
    NAME = "name"
    VALUE = "value"
    UNIT = "unit"
    mM = "mM"

    LABEL = "label"
    CIRCUIT = "circuit"
    INPUT_STATE = "input_state"
    SBH_URI = "sbh_uri"
    LAB_ID = "lab_id"
    AGAVE_URI = "agave_uri"

    STANDARD_TYPE = "standard_type"
    STANDARD_FOR = "standard_for"
    STANDARD_FLUORESCEIN = "FLUORESCEIN"
    STANDARD_MEDIA_BLANK = "MEDIA_BLANK"
    STANDARD_BEAD_FLUORESCENCE = "BEAD_FLUORESCENCE"
    STANDARD_BEAD_SIZE = "BEAD_SIZE"

    CONTROL_TYPE = "control_type"
    CONTROL_FOR = "control_for"
    CONTROL_BASELINE_MEDIA_PR = "BASELINE_MEDIA_PR"
    CONTROL_BASELINE = "BASELINE"
    CONTROL_EMPTY_VECTOR = "EMPTY_VECTOR"
    CONTROL_HIGH_FITC = "HIGH_FITC"
    CONTROL_CELL_DEATH_POS_CONTROL = "CELL_DEATH_POS_CONTROL"
    CONTROL_CELL_DEATH_NEG_CONTROL = "CELL_DEATH_NEG_CONTROL"
    CONTROL_CHANNEL = "control_channel"

    # sample attributes
    STANDARD_ATTRIBUTES = "standard_attributes"
    BEAD_MODEL = "bead_model"
    BEAD_BATCH = "bead_batch"

    # measurements
    MEASUREMENTS = "measurements"
    FILES = "files"
    FILE_ID = "file_id"
    FILE_LEVEL = "level"
    F_LEVEL_0 = "0"
    F_LEVEL_1 = "1"
    F_LEVEL_2 = "2"
    F_LEVEL_3 = "3"

    MEASUREMENT_TYPE = "measurement_type"
    MEASUREMENT_NAME = "measurement_name"
    SAMPLE_TMT_CHANNEL = "TMT_channel"
    MEASUREMENT_ID = "measurement_id"
    MEASUREMENT_GROUP_ID = "measurement_group_id"
    MEASUREMENT_LIBRARY_PREP = "library_prep"
    MEASUREMENT_LIBRARY_PREP_NORMAL = "NORMAL"
    MEASUREMENT_LIBRARY_PREP_MINIATURIZED = "MINIATURIZED"
    MT_RNA_SEQ = "RNA_SEQ"
    MT_DNA_SEQ = "DNA_SEQ"
    MT_FLOW = "FLOW"
    MT_IMAGE = "IMAGE"
    MT_SEQUENCING_CHROMATOGRAM = "SEQUENCING_CHROMATOGRAM"
    MT_EXPERIMENTAL_DESIGN = "EXPERIMENTAL_DESIGN"
    MT_PLATE_READER = "PLATE_READER"
    MT_PROTEOMICS = "PROTEOMICS"
    M_NAME = "name"
    M_TYPE = "type"
    M_LAB_LABEL = "lab_label"
    M_LAB_LABEL_RAW = "RAW"
    M_LAB_LABEL_PROCESSED = "PROCESSED"

    M_CHANNELS = "channels"
    M_INSTRUMENT_CONFIGURATION = "instrument_configuration"

    # Deprecated
    F_TYPE_SRAW = "SRAW"
    F_TYPE_FASTQ = "FASTQ"
    F_TYPE_CSV = "CSV"
    F_TYPE_FCS = "FCS"
    F_TYPE_ZIP = "ZIP"
    F_TYPE_PLAIN = "PLAIN"
    F_TYPE_MZML = "MZML"
    F_TYPE_MSF = "MSF"
    F_TYPE_ABI = "ABI"
    F_TYPE_BAI = "BAI"
    F_TYPE_BAM = "BAM"
    F_TYPE_JPG = "JPEG"

design_table = None
challenge_table = None

def map_experiment_reference(config, output_doc):
    global design_table
    global challenge_table

    if design_table is None:
        db = datacatalog.mongo.db_connection(config['mongodb'])
        design_table = db.experiment_designs
        challenge_table = db.challenges

    parent = None
    mapped = False
    try:
        # URI to id
        if SampleConstants.EXPERIMENT_REFERENCE_URL in output_doc:
            uri = output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL]
            sharing = "/edit?usp=sharing"
            if uri.endswith(sharing):
                uri = uri[:len(uri)-len(sharing)]
                output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = uri

            query = {}
            query["uri"] = uri

            matches = list(design_table.find(query).limit(1))
            for match in matches:
                parent = match["child_of"][0]
                output_doc[SampleConstants.EXPERIMENT_REFERENCE] = match["experiment_design_id"]
                break
            mapped = True
    except Exception as exc:
        raise Exception(exc)

    if not mapped:
        try:
            # id to URI
            if SampleConstants.EXPERIMENT_REFERENCE in output_doc:

                query = {}
                query["experiment_design_id"] = output_doc[SampleConstants.EXPERIMENT_REFERENCE]

                matches = list(design_table.find(query).limit(1))
                for match in matches:
                    parent = match["child_of"][0]
                    output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL] = match["uri"]
                    break

        except Exception as exc:
            raise Exception(exc)

    print("Mapped experiment reference {}".format(output_doc[SampleConstants.EXPERIMENT_REFERENCE]))
    print("Mapped experiment reference URL {}".format(output_doc[SampleConstants.EXPERIMENT_REFERENCE_URL]))

    # We have a reference, now, resolve the CP
    if parent is not None:
        query = {}
        query["uuid"] = parent
        matches = list(challenge_table.find(query).limit(1))

        for match in matches:
            print("Overwriting challenge problem with lookup {} ".format(match["id"]))
            output_doc[SampleConstants.CHALLENGE_PROBLEM] = match["id"]
            break

def convert_value_unit(value_unit):
    value_unit_split = value_unit.split(":")
    value = value_unit_split[0]
    if type(value) == int:
        value_unit_split[0] = int(value)
    elif type(value) == float:
        value_unit_split[0] = float(value)
    else:
        try:
            value_unit_split[0] = float(value)
        except Exception:
            value_unit_split[0] = str(value)
    return value_unit_split

def create_media_component(experiment_id, media_name, media_id, lab, sbh_query, value_unit=None):
    m_c_object = {}

    m_c_object[SampleConstants.NAME] = create_mapped_name(experiment_id, media_name, media_id, lab, sbh_query)
    if value_unit is not None:
        if type(value_unit) is int:
            value_unit_split = [value_unit]
        else:
            value_unit_split = convert_value_unit(value_unit)
        m_c_object[SampleConstants.VALUE] = value_unit_split[0]
        if len(value_unit_split) == 1:
            # no unit provided
            m_c_object[SampleConstants.UNIT] = SampleConstants.mM
        else:
            m_c_object[SampleConstants.UNIT] = value_unit_split[1]
            # apply some normalizations
            if m_c_object[SampleConstants.UNIT] == "micromolar":
                m_c_object[SampleConstants.UNIT] = "micromole"

    return m_c_object

# cache query lookups
sbh_cache = {}
mapping_failures = {}

def create_mapped_name(experiment_id, name_to_map, id_to_map, lab, sbh_query, strain=False):
    m_n_object = {}

    sbh_lab = None
    if lab == SampleConstants.LAB_GINKGO:
        sbh_lab = SD2Constants.GINKGO
    elif lab == SampleConstants.LAB_TX:
        sbh_lab = SD2Constants.TRANSCRIPTIC
    elif lab == SampleConstants.LAB_UWBF:
        sbh_lab = SD2Constants.BIOFAB
    elif lab == SampleConstants.LAB_CALTECH:
        # TODO: replace with SBHA constant when DR team updates
        sbh_lab = "CalTech"
    elif lab == SampleConstants.LAB_MARSHALL:
        # TODO: replace with SBHA constant when DR team updates
        sbh_lab = "Marshall"
    else:
        raise ValueError("Could not parse lab for SBH lookup: {}".format(lab))

    # SBH expects strings
    if type(id_to_map) == int:
        id_to_map = str(id_to_map)

    if id_to_map in sbh_cache:
        designs = sbh_cache[id_to_map]
    else:
        designs = sbh_query.query_designs_by_lab_ids(sbh_lab, [id_to_map], verbose=True)
        if len(designs) == 0 and id_to_map.startswith("https://hub.sd2e.org/user/sd2e/design"):
            print("Trying to map SBH URI directly")
            # Are we parsing a URI directly, not an internal lab id?
            query = """PREFIX sbol: <http://sbols.org/v2#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX sd2: <http://sd2e.org#>
            SELECT ?identity ?name ?id WHERE {{
                <https://hub.sd2e.org/user/sd2e/design/design_collection/1> sbol:member ?identity .
                ?identity dcterms:title ?name .
                VALUES (?identity) {{ (<{}>) }}
                VALUES (?id) {{ (<{}>) }}
            }}""".format(id_to_map, id_to_map)
            designs = sbh_query.fetch_SPARQL(SD2Constants.SD2_SERVER, query)
            # format like query_designs_by_lab_ids verbose
            designs = sbh_query.format_query_result(designs, ['identity', 'name'], 'id')
        sbh_cache[id_to_map] = designs

    if len(designs) > 0 and id_to_map in designs:
        values = designs[id_to_map]
        if isinstance(values, list):
            # we can only hold a single value here for now, take the first one
            # TODO DR/SBHA team fix this for current cases
            # and we make this throw an error for future runs
            values = values[0]
        # use URI and title from SBH
        sbh_uri = values["identity"]
        m_n_object[SampleConstants.SBH_URI] = sbh_uri
        m_n_object[SampleConstants.LABEL] = values["name"]
        # for strains, we have a SBH URI and can see if there is a circuit
        # associated with this strain
        if strain:
            circuit = query_circuit_from_strain(sbh_uri, sbh_query)
            # e.g. http://www.openmath.org/cd/logic1#nand
            if len(circuit) > 0:
                circuit = circuit[0]["gate_type"]
                if circuit.startswith(SampleConstants.LOGIC_PREFIX):
                    circuit = circuit.split(SampleConstants.LOGIC_PREFIX)[1].upper()
                    m_n_object[SampleConstants.CIRCUIT] = circuit

                    # grab the circuit's input state
                    input_state_bindings = query_input_state_from_strain(sbh_uri, sbh_query)
                    if len(input_state_bindings) > 0:
                        input_state = "".join(binding["level"]["value"] for binding in input_state_bindings)
                        m_n_object[SampleConstants.INPUT_STATE] = input_state
    else:
        # if we do not have a valid mapping, pass through the original lab name
        m_n_object[SampleConstants.LABEL] = name_to_map
        m_n_object[SampleConstants.SBH_URI] = "NO PROGRAM DICTIONARY ENTRY"
        if name_to_map not in mapping_failures:
            mapping_failures[name_to_map] = id_to_map
            mapping_type = "Reagent"
            if strain:
                mapping_type = "Strain"
            with open('create_mapped_name_failures.csv', 'a+') as unmapped:
                unmapped.write('"{}","{}","{}","{}","{}"\n'.format(experiment_id, sbh_lab, name_to_map, id_to_map, mapping_type))

    # m_n_object[SampleConstants.AGAVE_URI] =
    m_n_object[SampleConstants.LAB_ID] = namespace_lab_id(id_to_map, lab)
    return m_n_object

# temperature, time, etc.
def create_value_unit(value_unit):
    v_u_object = {}
    value_unit_split = convert_value_unit(value_unit)
    v_u_object[SampleConstants.VALUE] = value_unit_split[0]
    v_u_object[SampleConstants.UNIT] = value_unit_split[1]
    return v_u_object

# Query for a logic circuit (and, or, etc.) for a given strain
def query_circuit_from_strain(strain, sbh_query):

    _id = strain + SampleConstants.CIRCUIT
    if _id in sbh_cache:
        strain_circuit = sbh_cache[_id]
    else:
        strain_circuit = sbh_query.query_gate_logic([strain], pretty=True)
        sbh_cache[_id] = strain_circuit

    return strain_circuit

# Query for an input state for a circuit (00, 01, etc.) for a given strain
def query_input_state_from_strain(strain, sbh_query):

    _id = strain + SampleConstants.INPUT_STATE

    if _id in sbh_cache:
        strain_input_state = sbh_cache[_id]
    else:
        strain_input_state = sbh_query.query_gate_input_levels([strain])['results']['bindings']
        sbh_cache[_id] = strain_input_state

    return strain_input_state

# apply same logic as uploads manager to remove unicode and spaces
# all of the formatters currently route through here
def safen_filename(filename, no_unicode=True, no_spaces=True):
    return safen_path(filename, no_unicode=no_unicode, no_spaces=no_spaces)

# These experiments are already in the V2 database, and pre-date the namespacing change documented in
# https://gitlab.sd2e.org/sd2program/etl-pipeline-support/issues/12
# We need to skip that namespacing change for only these experiments, as changing their id structure
# will break the linkages between the jobs/file that have currently been executed and stored
# "Exp. Request - NC NAND Gate Iteration"
# "Exp. Request - NC NAND Gate Iteration"
# "CP Experimental Request - NovelChassis_NAND_Gate"
GINKGO_RNA_SEQ_EXPERIMENT_IDS = ["experiment.ginkgo.18256.18257", "experiment.ginkgo.18536.18537", "experiment.ginkgo.19283"]

def is_ginkgo_experiment_id(experiment_doc):
    return experiment_doc[SampleConstants.EXPERIMENT_ID] in GINKGO_RNA_SEQ_EXPERIMENT_IDS

# namespace against experiment id
def namespace_sample_id(sample_id, lab, experiment_doc):
    '''Prevents collisions amongst lab-specified sample_id'''
    # e.g. Ginkgo->TX sample lookups
    # Ginkgo specific skips (RNA_Seq)
    if experiment_doc is None or SampleConstants.EXPERIMENT_ID not in experiment_doc or \
        is_ginkgo_experiment_id(experiment_doc):
        return '.'.join(['sample', lab.lower(), str(sample_id)])
    else:
        return '.'.join(['sample', lab.lower(), str(sample_id), experiment_doc[SampleConstants.EXPERIMENT_ID]])

# namespace against sample id
def namespace_measurement_id(measurement_id, lab, sample_doc, experiment_doc):
    '''Prevents collisions amongst lab-specified measurement_id'''
    if experiment_doc is None or SampleConstants.EXPERIMENT_ID not in experiment_doc or \
        is_ginkgo_experiment_id(experiment_doc):
        return '.'.join(['measurement', lab.lower(), str(measurement_id)])
    else:
        return '.'.join(['measurement', lab.lower(), str(measurement_id), sample_doc[SampleConstants.SAMPLE_ID]])

# namespace against measurement id
def namespace_file_id(file_id, lab, measurement_doc, experiment_doc):
    '''Prevents collisions amongst lab-specified file_id'''
    if experiment_doc is None or SampleConstants.EXPERIMENT_ID not in experiment_doc or \
        is_ginkgo_experiment_id(experiment_doc):
        return '.'.join(['file', lab.lower(), str(file_id)])
    else:
        return '.'.join(['file', lab.lower(), str(file_id), measurement_doc[SampleConstants.MEASUREMENT_ID]])

def namespace_lab_id(lab_id, lab):
    '''Prevents collisions amongst lab-specified lab_id'''
    return '.'.join(['name', lab.lower(), str(lab_id)])

def namespace_experiment_id(lab_id, lab):
    '''Prevents collisions amongst lab-specified experiment_id'''
    return '.'.join(['experiment', lab.lower(), str(lab_id)])
