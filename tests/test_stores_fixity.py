import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
from .data.fixity import files

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/fixity/files')

def test_fixity_filetype(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = datacatalog.linkedstores.fixity.FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['type'] == ftype

def test_fixity_size(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = datacatalog.linkedstores.fixity.FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['size'] == tsize

def test_fixity_checksum(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = datacatalog.linkedstores.fixity.FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['checksum'] == cksum

@delete
def test_delete_fixity(mongodb_settings):
    fixity_store = datacatalog.linkedstores.fixity.FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        doc = fixity_store.find_one_by_id(name=fname)
        fixity_store.delete_document(doc['uuid'])
