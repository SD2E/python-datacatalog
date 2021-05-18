import os
import pytest
import sys
import yaml
import json
from agavepy.agave import Agave
from pprint import pprint

from datacatalog import agavehelpers

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.mark.parametrize("filename, system", [('/sample/tacc-cloud/123.txt', 'data-sd2e-community'),
                                              ('sample/tacc-cloud/123.txt', 'data-sd2e-community'),
                                              ('/sample/tacc-cloud/123.txt', None),
                                              ('sample/tacc-cloud/123.txt', None)
                                              ])
def test_mapped_posix_path(agave, filename, system):
    h = agavehelpers.AgaveHelper(agave)
    target = '/work2/projects/SD2E-Community/prod/data/sample/tacc-cloud/123.txt'
    pp = h.mapped_posix_path(filename, storage_system=system)
    assert pp == target

@pytest.mark.parametrize("filename, system, mapped_path",
                         [('/sample/tacc-cloud/123.txt',
                           'data-sd2e-community',
                           '/work2/projects/SD2E-Community/prod/data/sample/tacc-cloud/123.txt'),
                          ('/taconaut.txt',
                           'data-tacc-work2-sd2eadm',
                           '/work2/05201/sd2eadm/taconaut.txt'),
                          ('rabbit-9.jpg',
                           'data-sd2e-projects.sd2e-project-10',
                           '/work2/projects/SD2E-Community/prod/projects/sd2e-project-10/rabbit-9.jpg')])
def test_mapping_other_systems(agave, filename, system, mapped_path):
    h = agavehelpers.AgaveHelper(agave)
    pp = h.mapped_posix_path(filename, storage_system=system)
    assert pp == mapped_path

@pytest.mark.skipif(True, reason='Use of virtual_filesystem disabled"')
@pytest.mark.longrun
def test_listdir_posix(monkeypatch, agave):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', '50')
    h = agavehelpers.AgaveHelper(agave)
    listing = h.listdir_agave_posix('/sample/tacc-cloud/agavehelpers/upload', recurse=True, storage_system='virtual_filesystem', directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' in listing

@pytest.mark.longrun
def test_listdir_agave(monkeypatch, agave):
    h = agavehelpers.AgaveHelper(agave)
    listing = h.listdir_agave_native(
        '/sample/tacc-cloud/agavehelpers/upload',
        storage_system='data-sd2e-community',
        recurse=True, directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt' in listing

@pytest.mark.skipif(True, reason='Use of virtual_filesystem disabled"')
@pytest.mark.longrun
def test_listdir(monkeypatch, agave):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
        PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', '50')
    h = agavehelpers.AgaveHelper(agave)
    listing = h.listdir(
        '/sample/tacc-cloud/agavehelpers/upload', recurse=True, directories=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt' in listing

@pytest.mark.skipif(True, reason='Use of virtual_filesystem disabled"')
@pytest.mark.longrun
def test_listdir_only_files(monkeypatch, agave):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
        PARENT, 'tests/virtual_filesystem'))
    monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', '50')
    h = agavehelpers.AgaveHelper(agave)
    listing = h.listdir(
        '/sample/tacc-cloud/agavehelpers/upload', recurse=True, directories=False)
    assert '/sample/tacc-cloud/agavehelpers/upload/biofab/abcd' not in listing
    assert '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt' in listing

def test_from_agave_uri():
    asys, apath, afile = agavehelpers.from_agave_uri(
        'agave://data/taco/cabana.txt')
    assert asys == 'data'
    assert apath == '/taco'
    assert afile == 'cabana.txt'

def test_from_agave_uri_leading_double_slash():
    asys, apath, afile = agavehelpers.from_agave_uri(
        'agave://data//taco/cabana.txt')
    assert asys == 'data'
    assert apath == '/taco'
    assert afile == 'cabana.txt'

@pytest.mark.longrun
def test_isfile(monkeypatch, agave):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = agavehelpers.AgaveHelper(agave)
    t_isfile = h.isfile(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isfile is True
    t_isfile = h.isfile(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/')
    assert t_isfile is False

@pytest.mark.longrun
def test_isdir(monkeypatch, agave):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = agavehelpers.AgaveHelper(agave)
    t_isdir = h.isdir(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/')
    assert t_isdir is True
    t_isdir = h.isdir(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isdir is False

@pytest.mark.longrun
def test_exists_posix(monkeypatch, agave):
    # monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    # monkeypatch.setenv('CATALOG_ROOT_DIR', os.path.join(
    #     PARENT, 'tests/virtual_filesystem'))
    # monkeypatch.setenv('CATALOG_FILES_API_PAGESIZE', 50)
    h = agavehelpers.AgaveHelper(agave)
    t_isfile = h.exists(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt')
    assert t_isfile is True
    t_isfile = h.exists(
        '/sample/tacc-cloud/agavehelpers/upload/transcriptic/goodbye.txt')
    assert t_isfile is False
