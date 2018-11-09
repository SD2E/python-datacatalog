import os
import pytest
import sys
import yaml
import json

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/formats/files')

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
# from fixtures.mongodb import mongodb_settings, mongodb_authn
from data import formats

sys.path.insert(0, '/')
import datacatalog

@pytest.mark.parametrize("filename,classname", [('16122.json', 'Biofab'),
                                                ('62215.json', 'Biofab'),
                                                ('Novelchassis_Nand_gate_samples_20180919.json', 'Ginkgo'),
                                                ('r1btfnvt57bu7_r1btpq577ffhx_samples.json', 'Transcriptic'),
                                                ('transcriptic-samples.json', 'Transcriptic'),
                                                ('yeast-gates_samples20180929.json', 'Ginkgo')])
def test_format_imports(filename, classname):
    from datacatalog.formats import classify
    con = classify.get_converter(os.path.join(DATA_DIR, filename), expect=classname)
    assert con.name == classname
