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
from datacatalog.linkedstores.fixity import FixityStore
from datacatalog.linkedstores.file import FileStore

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(PARENT, 'tests/data/fixity/files')

@pytest.mark.parametrize("filename, level, ftype",
                         [('/uploads/biofab/201811/23801/provenance_dump.json', '0', 'BPROV'),
                          ('/products/sequence.fastq', '1', 'FASTQ')
                          ])
def test_fixity_pathmapping(monkeypatch, mongodb_settings, filename, level, ftype):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings)
    resp = fixity_store.index(filename)
    assert resp['level'] == level
    assert resp['type'] == ftype

def test_fixity_filetype(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['type'] == ftype

def test_fixity_size(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['size'] == tsize

def test_fixity_checksum(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['checksum'] == cksum

@pytest.mark.parametrize("generator_uuid", [
    ('1176bd3e-8666-547b-bc36-25a3b62fc271'),
    ('1179fdd6-71e0-504e-bab1-021ce3a72e35')])
def test_fixity_generated_by(monkeypatch, mongodb_settings, generator_uuid):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        # 1179fdd6-71e0-504e-bab1-021ce3a72e35 is tests-pytest
        resp = fixity_store.index(fname, generated_by=generator_uuid)
        assert generator_uuid in resp['generated_by']
        resp = fixity_store.index(fname, generated_by=[generator_uuid])
        assert generator_uuid in resp['generated_by']

def test_fixity_no_overrde_child_of(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings)
    file_store = FileStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        file_uuid = file_store.get_typeduuid(fname, binary=False)
        # This is one of the test files not indexed in the Fixity test collection
        resp = fixity_store.index(fname, child_of='105fb204-530b-5915-9fd6-caf88ca9ad8a')
        assert resp['child_of'] == [file_uuid]

@pytest.mark.parametrize("filename,fuuid", [
    ('/uploads/science-results.xlsx', '1166d16b-4c87-5ead-a25a-60ae90b527fb'),
    ('/uploads//science-results.xlsx', '1166d16b-4c87-5ead-a25a-60ae90b527fb')])
def test_fixity_normpath(mongodb_settings, filename, fuuid):
    base = FixityStore(mongodb_settings)
    identifier_string_uuid = base.get_typeduuid(filename, binary=False)
    assert identifier_string_uuid == fuuid

@delete
def test_delete_fixity(mongodb_settings):
    fixity_store = FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        doc = fixity_store.find_one_by_id(name=fname)
        fixity_store.delete_document(doc['uuid'])
