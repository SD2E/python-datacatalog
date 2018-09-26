import os
import pytest

from . import datacatalog
from .data.fixity import files

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/fixity/files')

def test_products_fixity_file_type(monkeypatch):
    monkeypatch.setenv('CATALOG_ROOT_DIR', DATA_DIR)
    for fname, cksum, tsize, ftype in files.TESTS:
        fixity = datacatalog.products.fixity.FileFixityInstance(fname, os.path.join(DATA_DIR, fname))
        fixity.sync()
        test_ftype = fixity.file_type()
        assert test_ftype == ftype

def test_products_fixity_size(monkeypatch):
    monkeypatch.setenv('CATALOG_ROOT_DIR', DATA_DIR)
    for fname, cksum, tsize, ftype in files.TESTS:
        fixity = datacatalog.products.fixity.FileFixityInstance(
            fname, os.path.join(DATA_DIR, fname))
        fixity.sync()
        test_size = fixity.size()
        assert test_size == tsize

def test_products_fixity_checksum(monkeypatch):
    monkeypatch.setenv('CATALOG_ROOT_DIR', DATA_DIR)
    for fname, cksum, tsize, ftype in files.TESTS:
        fixity = datacatalog.products.fixity.FileFixityInstance(
            fname, os.path.join(DATA_DIR, fname))
        fixity.sync()
        test_cksum = fixity.checksum()
        assert test_cksum == cksum

