import os
import sys
import yaml
import pytest

CWD = os.getcwd()

@pytest.mark.smoktest
def test_load_config_yml():
    """Ensure local config.yml is available and loadable"""
    with open(os.path.join(CWD, 'config.yml'), "r") as conf:
        y = yaml.safe_load(conf)
        assert isinstance(y, dict)
