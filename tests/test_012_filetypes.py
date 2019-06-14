import os
import pytest
import sys
import yaml
import json
import time
import tempfile
import warnings
from pprint import pprint
from . import longrun, delete

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from .fixtures.agave import agave, credentials
from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/filetypes')

@pytest.mark.parametrize("filename, label",
                         [('/uploads/biofab/201811/23801/provenance_dump.json', 'BPROV'),
                          ('/products/sequence.fastq', 'FASTQ'),
                          ('/products/sequence-align.bedgraph', 'BEDGRAPH'),
                          ('/products/file.ASDFGHJK123456', 'UNKNOWN')
                          ])
def test_infer_filetype(filename, label):
    ft = datacatalog.filetypes.infer_filetype(filename, check_exists=False)
    assert ft.label == label

