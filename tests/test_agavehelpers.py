import os
import pytest

from . import datacatalog

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_listdir_posix(monkeypatch):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper()
    listing = h.listdir_agave_posix('/sample/tacc-cloud/agavehelpers/upload', recurse=True, storage_system='virtual_filesystem', directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' in listing

def test_listdir_agave(monkeypatch):
    h = datacatalog.agavehelpers.AgaveHelper()
    listing = h.listdir_agave_native(
        '/sample/tacc-cloud/agavehelpers/upload', recurse=True, directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' in listing

def test_listdir(monkeypatch):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
        PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper()
    listing = h.listdir(
        '/sample/tacc-cloud/agavehelpers/upload', recurse=True, directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' in listing

def test_from_agave_uri():
    asys, apath, afile = datacatalog.agavehelpers.from_agave_uri(
        'agave://data/taco/cabana.txt')
    assert asys == 'data'
    assert apath == '/taco'
    assert afile == 'cabana.txt'
