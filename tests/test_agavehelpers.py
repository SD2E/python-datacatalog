import os
import pytest

from . import datacatalog

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

# def test_from_agave_uri():
#     asys, apath, afile = datacatalog.agavehelpers.from_agave_uri(
#         'agave://data/taco/cabana.txt')
#     assert asys == 'data'
#     assert apath == '/taco'
#     assert afile == 'cabana.txt'

def test_listdir_posix(monkeypatch):
    monkeypatch.setenv('CATALOG_STORAGE_SYSTEM', 'virtual_filesystem')
    monkeypatch.setenv('CATALOG_STORAGE_PREFIX', os.path.join(PARENT, 'virtual_filesystem'))
    monkeypatch.setenv('CATALOG_STORAGE_PAGESIZE', 50)
    ls = datacatalog.agavehelpers.__listdir_agave_posix('/uploads', recurse=True, storage_system='virtual_filesystem', directories=True)
    assert ls == []
