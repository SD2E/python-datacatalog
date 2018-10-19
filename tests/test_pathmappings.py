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
from data import pathmappings

sys.path.insert(0, '/')
import datacatalog

def test_prefix_for_level():
    for pth, pfx, lev in pathmappings.CASES:
        assert datacatalog.pathmappings.prefix_for_level(lev) == pfx

def test_level_for_prefix():
    for path, prefix, level in pathmappings.CASES:
        assert datacatalog.pathmappings.level_for_prefix(prefix) == level

def test_level_for_filepath():
    for path, prefix, level in pathmappings.CASES:
        assert datacatalog.pathmappings.level_for_filepath(path) == level
