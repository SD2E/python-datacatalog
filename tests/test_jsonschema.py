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

@pytest.mark.parametrize("jsonfile", [('samples-biofab.json'), ('samples-ginkgo.json'), ('samples-transcriptic.json')])
def test_validate_sample_set(jsonfile):
    res = resolver(schema='sample_set')
    jsonpath = os.path.join(DATA_DIR, jsonfile)
    instance = json.load(open(jsonpath, 'r'))
    assert jsonschema.validate(instance, res) is True
