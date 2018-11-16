import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .data import pathmappings
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_prefix_for_level():
    for pth, pfx, lev, store in pathmappings.CASES:
        assert datacatalog.pathmappings.prefix_for_level(lev) == pfx

def test_level_for_prefix():
    for path, prefix, level, store in pathmappings.CASES:
        assert datacatalog.pathmappings.level_for_prefix(prefix) == level

def test_level_for_filepath():
    for path, prefix, level, store in pathmappings.CASES:
        assert datacatalog.pathmappings.level_for_filepath(path) == level

def test_store_for_level():
    for path, prefix, level, store in pathmappings.CASES:
        assert datacatalog.pathmappings.store_for_level(level) == store

def test_abspath_maps():
    for filename, abspath in pathmappings.ABSPATHS:
        assert datacatalog.pathmappings.abspath(filename) == abspath

def test_relativize():
    for filename, abspath in pathmappings.ABSPATHS:
        assert datacatalog.pathmappings.relativize(abspath) == datacatalog.pathmappings.relativize(filename)
