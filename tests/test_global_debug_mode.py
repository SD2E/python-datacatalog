import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_debug_false(monkeypatch):
    monkeypatch.setenv('LOCALONLY', '0')
    mode = datacatalog.debug_mode.debug_mode()
    assert mode is False
    monkeypatch.setenv('LOCALONLY', '0')

def test_debug_true(monkeypatch):
    monkeypatch.setenv('LOCALONLY', '1')
    mode = datacatalog.debug_mode.debug_mode()
    assert mode is True
    monkeypatch.setenv('LOCALONLY', '0')
