import json
import os
from pprint import pprint

from . import CASES
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'pipeline')

def get_files():
    for filename, uuid, valid in CASES:
        data = json.load(open(os.path.join(DATA_DIR, filename), 'r'))
        test_struct = {'data': data, 'uuid': uuid, 'valid': valid}
        yield test_struct

