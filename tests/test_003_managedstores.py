import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .data import pathmappings
from datacatalog import stores

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def tests_levels_invalid():
    with pytest.raises(ValueError):
        stores.Level('ABCDEF')

def tests_levels_valid():
    for pth, pfx, level, store in pathmappings.CASES:
        stores.Level(level)

@pytest.mark.skipif(True, reason='No longer map levels to dirctory prefixes alone"')
def test_prefixes_for_level():
    for pth, pfx, level, store in pathmappings.CASES:
        assert pfx in stores.ManagedStores.prefixes_for_level(level)

@pytest.mark.skipif(True, reason='No longer map stores to levels"')
def test_store_for_level():
    for path, prefix, level, store in pathmappings.CASES:
        assert stores.ManagedStores.store_for_level(level) == store

@pytest.mark.skipif(True, reason='No longer map stores to prefixes via level"')
def test_store_for_prefix():
    for path, prefix, level, store in pathmappings.CASES:
        assert stores.ManagedStores.store_for_prefix(prefix) == store

@pytest.mark.skipif(True, reason='No longer map stores to prefixes via level"')
def test_levels_for_prefix():
    for path, prefix, level, store in pathmappings.CASES:
        assert level in stores.ManagedStores.levels_for_prefix(prefix)

@pytest.mark.skipif(True, reason='No longer map stores to prefixes via level"')
def test_levels_for_filepath():
    for path, prefix, level, store in pathmappings.CASES:
        try:
            assert level in stores.ManagedStores.levels_for_filepath(path)
        except stores.ManagedStoreError:
            pass

@pytest.mark.skipif(True, reason='No longer map stores to prefixes via level"')
def test_stores_for_filepath():
    for path, prefix, level, store in pathmappings.CASES:
        try:
            assert store in stores.ManagedStores.stores_for_filepath(path)
        except stores.ManagedStoreError:
            pass

@pytest.mark.skipif(True, reason='Method abspath can only be used via an AgaveHelper"')
def test_abspath_maps():
    for filename, abspath in pathmappings.ABSPATHS:
        assert stores.abspath(filepath=filename) == abspath
