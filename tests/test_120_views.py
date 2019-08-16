import os
import pytest
import json
import jsonschema

from datacatalog import views

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/views')

@pytest.mark.skip(reason="Schema support in views was retired")
def test_views_get_schemas():
    schemas = views.schemas.get_schemas()
    assert isinstance(schemas, dict)
    assert schemas != dict()

def test_views_get_aggregations():
    aggs = views.aggregations.get_aggregations()
    assert isinstance(aggs, dict)
    assert aggs != dict()
