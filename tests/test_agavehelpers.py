import os
import pytest
import sys
import yaml
import json
from agavepy.agave import Agave

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)

from fixtures.agave import agave, credentials
sys.path.insert(0, '/')
import datacatalog


def test_listdir_posix(monkeypatch, agave):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', '50')
    h = datacatalog.agavehelpers.AgaveHelper(agave)
    listing = h.listdir_agave_posix('/sample/tacc-cloud/agavehelpers/upload', recurse=True, storage_system='virtual_filesystem', directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' in listing

def test_listdir_agave(monkeypatch, agave):
    h = datacatalog.agavehelpers.AgaveHelper(agave)
    listing = h.listdir_agave_native(
        '/sample/tacc-cloud/agavehelpers/upload', recurse=True, directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' in listing

def test_listdir(monkeypatch, agave):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
        PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', '50')
    h = datacatalog.agavehelpers.AgaveHelper(agave)
    listing = h.listdir(
        '/sample/tacc-cloud/agavehelpers/upload', recurse=True, directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' in listing

def test_listdir_only_files(monkeypatch, agave):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
        PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', '50')
    h = datacatalog.agavehelpers.AgaveHelper(agave)
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

def test_isfile(monkeypatch, agave):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper(agave)
    t_isfile = h.isfile(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isfile is True
    t_isfile = h.isfile(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/')
    assert t_isfile is False

def test_isdir(monkeypatch, agave):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper(agave)
    t_isdir = h.isdir(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/')
    assert t_isdir is True
    t_isdir = h.isdir(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isdir is False

def test_exists_posix(monkeypatch, agave):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = datacatalog.agavehelpers.AgaveHelper(agave)
    t_isfile = h.exists(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isfile is True
    t_isfile = h.exists(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/goodbye.txt')
    assert t_isfile is False
