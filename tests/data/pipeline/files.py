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

LOADS = [
    ('manual-upload.json', '105c0c55-62d0-50ed-a6eb-aa9cd8038d72'),
    ('metadata_capture.json', '1052ac87-7d61-50d1-8a04-2412b2695beb'),
    ('novel_chassis_rnaseq.json', '1050e16b-d81c-54f7-ad82-36ed4de27c11'),
    ('platereader.json', '1050fc59-1363-51eb-8686-f24e0b3d0d86'),
    ('rnaseq.json', '10564142-a403-58ba-af9e-5b80e8f17d57'),
    ('tacobot.json', '10564142-a403-58ba-af9e-5b80e8f17d57'),
    ('urrutia-aggregation.json', '10564142-a403-58ba-af9e-5b80e8f17d57'),
    ('urrutia-multiqc.json', '10564142-a403-58ba-af9e-5b80e8f17d57'),
]
