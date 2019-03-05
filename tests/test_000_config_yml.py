import os
import sys
import yaml
import json
from . import longrun, delete, bootstrap, smoketest

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@smoketest
def test_config_yml_smoke():
    """Ensure local config.yml is available and loadable"""
    with open(os.path.join(CWD, 'config.yml'), "r") as conf:
        y = yaml.safe_load(conf)
        assert isinstance(y, dict)
