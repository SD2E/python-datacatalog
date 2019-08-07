import pytest
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)
from scripts import build_schemas

@pytest.mark.networked
def test_regenerate_schemas(env_make_tests):
    res = build_schemas.regenerate()
    assert res is True
