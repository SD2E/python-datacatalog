import pytest
import os
import sys
from attrdict import AttrDict

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)
from scripts import build_experiment_designs

@pytest.mark.networked
def test_regenerate_experiment_des(env_make_tests, mongodb_settings):
    """Directly call the regnerate() method to sync experiment_design records
    """
    args = AttrDict({'environment': 'localhost'})
    resp = build_experiment_designs.regenerate(
        args, update_catalog=True, mongodb=mongodb_settings)
    assert resp is True
