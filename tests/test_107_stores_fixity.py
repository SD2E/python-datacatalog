import os
import pytest
import sys
import yaml
import json
import time
import tempfile
from pprint import pprint
from . import longrun, delete

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
from .data.fixity import files
from datacatalog.linkedstores.fixity import FixityStore, RateLimitExceeded
from datacatalog.linkedstores.file import FileStore
from datacatalog.linkedstores.fixity.indexer import FixityIndexer

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

@longrun
def test_fixity_indexer_cache(monkeypatch):
    """Confirms that caching os.stats() makes FixityIndexer faster
    """
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    # Run with cache ON
    elapsed = list()
    for use_cache in [False, True]:
        start_time = time.time()
        for reps in range(0, 2000):
            for fname, cksum, tsize, ftype in files.NO_SURPRISES:
                abs_fname = os.path.join(DATA_DIR, fname)
                rel_fname = os.path.join('tests/data/fixity/files', fname)
                fidx = FixityIndexer(abs_filename=os.path.abspath(abs_fname), name=rel_fname, cache_stat=use_cache)
                fidx.sync()
                assert fidx.type == ftype, 'wrong type for {}'.format(fname)
        elapsed.append(time.time() - start_time)
    assert elapsed[0] > elapsed[1], 'Avoiding stat() had no apparent effect'

@longrun
def test_fixity_indexer_cache_no_buffering(monkeypatch):
    """Confirms os.stats() cache makes FixityIndexer faster without file.read buffering
    """
    TMPDIR = tempfile.mkdtemp()
    FILE_SIZE = 65536000
    elapsed = list()
    for use_cache in [False, True]:
        start_time = time.time()
        for fname, cksum, tsize, ftype in files.NO_SURPRISES:
            abs_fname = os.path.join(TMPDIR, fname)
            fout = open(abs_fname, 'wb', 0)
            fout.write(os.urandom(FILE_SIZE))
            fout.close()
            fidx = FixityIndexer(abs_filename=abs_fname, name=fname, cache_stat=use_cache)
            fidx.sync()
            os.unlink(abs_fname)
        elapsed.append(time.time() - start_time)
    assert elapsed[0] > elapsed[1], 'Avoiding stat() had no apparent effect'

@longrun
def test_fixity_indexer_cache_blocksize(monkeypatch):
    """This profiles the impact of block size on fixity operations

    It may fail idiopathicallydue to local OS or host operations that consume
    disk and CPU IO.
    """
    TMPDIR = tempfile.mkdtemp()
    FILE_SIZE = 32000000
    REPS = 5
    BLOCK_SIZES = [8000, 16000, 32000, 64000, 128000, 256000, 512000]
    elapsed = list()
    for rep in REPS:
        rep_elapsed = list()
        for block_size in BLOCK_SIZES:
            start_time = time.time()
            for fname, cksum, tsize, ftype in files.NO_SURPRISES:
                abs_fname = os.path.join(TMPDIR, fname)
                fout = open(abs_fname, 'wb', 0)
                fout.write(os.urandom(FILE_SIZE))
                fout.close()
                fidx = FixityIndexer(abs_filename=abs_fname, name=fname,
                                     cache_stat=True, block_size=block_size)
                fidx.sync()
                os.unlink(abs_fname)
            rep_elapsed.append((block_size, time.time() - start_time))
        elapsed.append(rep_elapsed)
    prev_elapse = -1
    deltas = list()
    for buf, elapse in elapsed:
        if prev_elapse > 0:
            pct_delta = 100 * (1 - (elapse - prev_elapse) / prev_elapse)
            assert pct_delta > 100, 'No more ROI on buffer size beyond {}'.format(buf)
            deltas.append((buf, pct_delta))
        prev_elapse = elapse

def test_fixity_limit_rate_exception(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings, batch_size=5, batch_window=1, except_on_limit=True)
    with pytest.raises(RateLimitExceeded):
        for fname, cksum, tsize, ftype in files.TESTS:
            resp = fixity_store.index(fname)
            assert resp['type'] == ftype

def test_fixity_limit_rate_pause(monkeypatch, mongodb_settings):
    monkeypatch.setenv('DEBUG_STORES_NATIVE_PREFIX', DATA_DIR)
    fixity_store = FixityStore(mongodb_settings, batch_size=5, batch_window=1, except_on_limit=False)
    for fname, cksum, tsize, ftype in files.TESTS:
        resp = fixity_store.index(fname)
        assert resp['type'] == ftype

@delete
def test_fixity_delete(mongodb_settings):
    fixity_store = FixityStore(mongodb_settings)
    for fname, cksum, tsize, ftype in files.TESTS:
        doc = fixity_store.find_one_by_id(name=fname)
        fixity_store.delete_document(doc['uuid'])
