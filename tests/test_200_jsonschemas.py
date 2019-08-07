import pytest
import os
import json
import jsonschema
from datacatalog import jsonschemas

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/jsonschema')

# def test_identifiers_typeduuid_get_schemas():
#     schemas = identifiers.typeduuid.schemas.get_schemas()
#     assert isinstance(schemas, dict)
#     for k, v in schemas.items():
#         assert isinstance(v, str)

def test_get_allschemas_filter_all():
    schemas = jsonschemas.get_all_schemas(filters=['will-never-be-valid'])
    assert isinstance(schemas, dict)
    assert len(list(schemas.keys())) == 0

def test_get_allschemas_filter_one():
    schemas = jsonschemas.get_all_schemas(filters=['linkedstores.basestore'])
    assert isinstance(schemas, dict)
    # the object and document schemas
    assert len(list(schemas.keys())) == 2

def test_get_allschemas():
    schemas = jsonschemas.get_all_schemas()
    assert isinstance(schemas, dict)
    assert len(list(schemas.keys())) > 0

def test_validate_allschemas_json():
    SCHEMAS_PATH = os.path.join(PARENT, 'schemas')
    schemas = os.listdir(SCHEMAS_PATH)
    for schema in schemas:
        if schema.endswith('.json'):
            fname = os.path.join(SCHEMAS_PATH, schema)
            sch = open(fname, 'r')
            # Can load as JSON
            schj = json.load(sch)
            assert isinstance(schj, dict)

@pytest.mark.longrun
@pytest.mark.networked
@pytest.mark.parametrize("draft,response", [
    ('draft-07.json', True),
    ('draft-06.json', True),
    ('draft-04.json', False),
    ('draft-03.json', False),
    ('draft-02.json', False),
    ('draft-01.json', False)])
def test_validate_allschemas_drafts(draft, response):
    SCHEMAS_PATH = os.path.join(PARENT, 'schemas')
    schemas = os.listdir(SCHEMAS_PATH)
    draft_schema = json.load(open(os.path.join(DATA_DIR, draft), 'r'))
    raised_exceptions = list()
    for schema in schemas:
        if schema.endswith('.json'):
            fname = os.path.join(SCHEMAS_PATH, schema)
            sch = open(fname, 'r')
            # Can load as JSON
            schj = json.load(sch)
            try:
                jsonschema.validate(schj, draft_schema)
            except Exception as exc:
                raised_exceptions.append((schema, exc))
    if response is True:
        assert len(raised_exceptions) == 0, "Unexpected validation or schema errors found: %r" % raised_exceptions
    else:
        assert len(raised_exceptions) > 0, "Validation or schema was expected to fail but did not"

@pytest.mark.networked
@pytest.mark.parametrize("draft,response", [
    ('draft-07.json', True),
    ('draft-06.json', True)])
def test_validate_allschemas_drafts_tenacity(draft, response):
    SCHEMAS_PATH = os.path.join(PARENT, 'schemas')
    schemas = os.listdir(SCHEMAS_PATH)
    draft_schema = json.load(open(os.path.join(DATA_DIR, draft), 'r'))
    raised_exceptions = list()
    for schema in schemas:
        if schema.endswith('.json'):
            fname = os.path.join(SCHEMAS_PATH, schema)
            sch = open(fname, 'r')
            # Can load as JSON
            schj = json.load(sch)
            try:
                jsonschemas.validate(schj, draft_schema)
            except Exception as exc:
                raised_exceptions.append((schema, exc))
    if response is True:
        assert len(raised_exceptions) == 0, "Unexpected validation or schema errors found: %r" % raised_exceptions
    else:
        assert len(raised_exceptions) > 0, "Validation or schema was expected to fail but did not"
