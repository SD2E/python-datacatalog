import os
import pytest
import sys
import yaml
import json

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
from fixtures.mongodb import mongodb_settings, mongodb_authn
sys.path.insert(0, '/')
import scripts

def test_regenerate_schemas(monkeypatch):
    monkeypatch.setenv('MAKETESTS', '1')
    res = scripts.build_schemas.regenerate()
    assert res is True
