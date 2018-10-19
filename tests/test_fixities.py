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
from data.fixity import files
sys.path.insert(0, '/')
import datacatalog

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/fixity/files')

def test_fixity_file_type(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = datacatalog.linkedstores.fixities.FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['type'] == ftype

# def test_products_fixity_size(monkeypatch):
#     monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
#     for fname, cksum, tsize, ftype in files.TESTS:
#         fixity = datacatalog.products.fixity.FileFixityInstance(
#             fname, os.path.join(DATA_DIR, fname))
#         fixity.sync()
#         test_size = fixity.size()
#         assert test_size == tsize

# def test_products_fixity_checksum(monkeypatch):
#     monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
#     for fname, cksum, tsize, ftype in files.TESTS:
#         fixity = datacatalog.products.fixity.FileFixityInstance(
#             fname, os.path.join(DATA_DIR, fname))
#         fixity.sync()
#         test_cksum = fixity.checksum()
#         assert test_cksum == cksum
