import os
import pytest

from . import datacatalog
from agavepy.agave import Agave

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

def test_listdir_only_files(monkeypatch):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
        PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper()
    listing = h.listdir(
        '/sample/tacc-cloud/agavehelpers/upload', recurse=True, directories=False)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' not in listing
    assert '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt' in listing

def test_from_agave_uri():
    asys, apath, afile = datacatalog.agavehelpers.from_agave_uri(
        'agave://data/taco/cabana.txt')
    assert asys == 'data'
    assert apath == '/taco'
    assert afile == 'cabana.txt'

def test_isfile(monkeypatch):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper()
    t_isfile = h.isfile(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isfile is True
    t_isfile = h.isfile(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/')
    assert t_isfile is False

def test_isdir(monkeypatch):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper()
    t_isdir = h.isdir(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/')
    assert t_isdir is True
    t_isdir = h.isdir(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isdir is False

def test_exists_posix(monkeypatch):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper()
    t_isfile = h.exists(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isfile is True
    t_isfile = h.exists(
            '/sample/tacc-cloud/agavehelpers/upload/transcriptic/goodbye.txt')
    assert t_isfile is False
