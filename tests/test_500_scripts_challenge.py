import os
import pytest
import sys
import yaml
import json
from agavepy.agave import Agave
from pprint import pprint
from . import longrun, networked, delete
from .fixtures import agave, credentials, mongodb_settings, mongodb_authn
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
# sys.path.insert(0, PARENT)
from scripts import build_challenge_problems

# @networked
def test_regenerate_cp(monkeypatch, mongodb_settings):
    monkeypatch.setenv('MAKETESTS', '1')
    resp = build_challenge_problems.regenerate(
        update_catalog=True, mongodb=mongodb_settings)
    assert resp is True
