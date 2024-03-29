import os
import json
import pytest
import jsonschema
from datacatalog.jsonschemas.schema import JSONSchemaBaseObject

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/sampleset')

def resolver(base_uri=JSONSchemaBaseObject.BASEREF, schema='sample_set'):
    remote_uri = base_uri + schema + '.json'
    return jsonschema.RefResolver('', '').resolve_remote(remote_uri)

@pytest.mark.networked
@pytest.mark.parametrize("jsonfile", [('17016_87542.json'), ('20249.json'), ('95463.json'), ('Novelchassis_Nand_gate_controls.json'), ('Novelchassis_Nand_gate_samples.json'), ('r1btfp5k2edgn_r1btpym75nsdh_samples.json'), ('r1bzc55fpurbj.json'), ('samples_nc.json'), ('62215.json'), ('r1bsmgdayg2yq_r1bsu7tb7bsuk_samples.json')])
def test_validate_sample_set(jsonfile):
    class formatChecker(jsonschema.FormatChecker):
        def __init__(self):
            jsonschema.FormatChecker.__init__(self)

    res = resolver(schema='sample_set')
    jsonpath = os.path.join(DATA_DIR, jsonfile)
    instance = json.load(open(jsonpath, 'r'))
    assert jsonschema.validate(
        instance, res, format_checker=formatChecker()) is None
