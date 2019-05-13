import os
import pytest
import sys
import yaml
import json
import jsonschema

from pprint import pprint
from . import longrun, delete
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/views')

@pytest.mark.skip(reason="Schema support in views was retired")
def test_views_get_schemas():
    schemas = datacatalog.views.schemas.get_schemas()
    assert isinstance(schemas, dict)
    assert schemas != dict()

def test_views_get_aggregations():
    aggs = datacatalog.views.aggregations.get_aggregations()
    assert isinstance(aggs, dict)
    assert aggs != dict()
