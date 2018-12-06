import json
import os
from pprint import pprint

from . import CASES, EVENTS, FAILED_EVENTS
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'pipelinejob')

def get_jobs():
    for filename, uuid, valid in CASES:
        data = json.load(open(os.path.join(DATA_DIR, filename), 'r'))
        test_struct = {'data': data, 'uuid': uuid, 'valid': valid}
        yield test_struct

def get_events():
    for filename, uuid, valid in EVENTS:
        data = json.load(open(os.path.join(DATA_DIR, filename), 'r'))
        test_struct = {'data': data, 'uuid': uuid, 'valid': valid}
        yield test_struct

def get_events_wrong_uuid():
    for filename, uuid, valid in FAILED_EVENTS:
        data = json.load(open(os.path.join(DATA_DIR, filename), 'r'))
        test_struct = {'data': data, 'uuid': uuid, 'valid': valid}
        yield test_struct
