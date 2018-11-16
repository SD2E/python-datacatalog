import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures import mongodb_settings, mongodb_authn
from .data import formats
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
import scripts

def test_regenerate_schemas(monkeypatch):
    monkeypatch.setenv('MAKETESTS', '1')
    res = scripts.build_schemas.regenerate()
    assert res is True
