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

def test_regenerate_experiment_refs(monkeypatch, mongodb_settings):
    monkeypatch.setenv('MAKETESTS', '1')
    resp = scripts.build_experiment_references.regenerate(
        update_catalog=True, mongodb=mongodb_settings)
    assert resp is True
