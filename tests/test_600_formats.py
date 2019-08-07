import os
import pytest

from datacatalog import formats as formats_module
from datacatalog import jsonschemas
from .data import formats

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/formats/files')

def test_formats_independent_imports():
    # Ensure classify and other utils can be independently imported
    assert hasattr(formats_module, 'classify')

@pytest.mark.parametrize("filename,classname,tenant,project", formats.files.CLASSIFY)
def test_formats_classify(filename, classname, tenant, project):
    con = formats_module.classify.get_converter(
        os.path.join(DATA_DIR, filename), expect=classname)
    assert con.name == classname
    assert con.tenant == tenant
    assert con.project == project

def test_formats_converters_have_schema_data():
    convs = formats_module.classify.get_converters()
    for conv in convs:
        assert conv.version is not None
        schema = conv.get_classifier_schema()
        assert isinstance(schema, dict)

def test_formats_get_schemas():
    schemas = jsonschemas.get_all_schemas(filters=['formats'])
    assert isinstance(schemas, dict)
    # the object and document schemas
    assert len(list(schemas.keys())) > 0
