import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
# import datacatalog
import jsonschema

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/sampleset')

JSONSCHEMA_BASE_URL = 'https://sd2e.github.io/python-datacatalog/schemas/'
# JSONSCHEMA_BASE_URL = 'https://catalog.sd2e.org/schemas/'

def resolver(base_uri=JSONSCHEMA_BASE_URL, schema='sample_set'):
    remote_uri = base_uri + schema + '.json'
    print('REMOTE_URI', remote_uri)
    return jsonschema.RefResolver('', '').resolve_remote(remote_uri)

@pytest.mark.parametrize("jsonfile", [('17016_87542.json'), ('20249.json'), ('95463.json'), ('Novelchassis_Nand_gate_controls.json'), ('Novelchassis_Nand_gate_samples.json'), ('r1btfp5k2edgn_r1btpym75nsdh_samples.json'), ('r1bzc55fpurbj.json'), ('samples_nc.json')])
def test_validate_sample_set(jsonfile):
    print('TEST', jsonfile)
    res = resolver(schema='sample_set')
    jsonpath = os.path.join(DATA_DIR, jsonfile)
    instance = json.load(open(jsonpath, 'r'))
    assert jsonschema.validate(instance, res) is None
