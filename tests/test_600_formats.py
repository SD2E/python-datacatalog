import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .data import formats
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/formats/files')

def test_formats_independent_imports():
    # Ensure classify and other utils can be independently imported
    from datacatalog.formats import classify
    return True

@pytest.mark.parametrize("filename,classname", [('16122.json', 'Biofab'),
                                                ('62215.json', 'Biofab'),
                                                ('Novelchassis_Nand_gate_samples_20180919.json', 'Ginkgo'),
                                                ('r1btfnvt57bu7_r1btpq577ffhx_samples.json', 'Transcriptic'),
                                                ('transcriptic-samples.json', 'Transcriptic'),
                                                ('yeast-gates_samples20180929.json', 'Ginkgo')])
def test_formats_classify(filename, classname):
    from datacatalog.formats import classify
    con = classify.get_converter(os.path.join(DATA_DIR, filename), expect=classname)
    assert con.name == classname

def test_formats_converters_have_schema_data():
    from datacatalog.formats import classify
    convs = classify.get_converters()
    for conv in convs:
        assert conv.version is not None
        schema = conv.get_classifier_schema()
        assert isinstance(schema, dict)

def test_formats_get_schemas():
    schemas = datacatalog.jsonschemas.get_all_schemas(filters=['formats'])
    assert isinstance(schemas, dict)
    # the object and document schemas
    assert len(list(schemas.keys())) > 0
