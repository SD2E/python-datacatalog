import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
from .fixtures.agave import agave, credentials
import datacatalog
from .data import pipelinejob
from datacatalog.linkedstores.pipelinejob import PipelineJobStore, exceptions

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_job_db_init(mongodb_settings):
    base = PipelineJobStore(mongodb_settings)
    assert base is not None

def test_job_db_heritable_schema(mongodb_settings):
    base = PipelineJobStore(mongodb_settings)
    assert 'archive_path' in base.get_indexes()
    # exclude via NEVER_INDEX_FIELDS
    assert 'data' not in base.get_indexes()

def test_job_db_list_collection_names(mongodb_settings):
    base = PipelineJobStore(mongodb_settings)
    assert base.db.list_collection_names() is not None

def test_job_schema(mongodb_settings):
    base = PipelineJobStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_job_name(mongodb_settings):
    base = PipelineJobStore(mongodb_settings)
    assert base.name == 'jobs'

def test_job_uuid_tytpe(mongodb_settings):
    base = PipelineJobStore(mongodb_settings)
    assert base.get_uuid_type() == 'pipelinejob'

def test_job_create(mongodb_settings, monkeypatch):
    monkeypatch.setenv('LOCALONLY', '1')
    base = PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_jobs():
        resp = base.create(data_struct['data'])
        assert resp['uuid'] == data_struct['uuid']

def test_job_handle_event_ok(mongodb_settings, monkeypatch):
    monkeypatch.setenv('LOCALONLY', '1')
    base = PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_events():
        resp = base.handle(data_struct['data'])
        assert resp['uuid'] == data_struct['uuid']

def test_job_handle_event_wrong_uuid(mongodb_settings, monkeypatch):
    monkeypatch.setenv('LOCALONLY', '1')
    base = PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_events_wrong_uuid():
        with pytest.raises(exceptions.UnknownJob):
            base.handle(data_struct['data'])

def test_job_fsm_state_png(mongodb_settings, monkeypatch):
    try:
        import pygraphviz
        monkeypatch.setenv('LOCALONLY', '1')
        base = PipelineJobStore(mongodb_settings)
        for data_struct in pipelinejob.get_jobs():
                graf = base.fsm_state_png(data_struct['uuid'])
                # This is the signature of PNG - \x89PNG
                assert 'iVBOR' in graf.decode('utf-8')
    except ModuleNotFoundError:
        pass

# def test_job_write_key_ok(mongodb_settings):
#     base = PipelineJobStore(mongodb_settings)
#     for data_struct in pipelinejob.get_jobs():
#         key = 'keykeykey'
#         val = 'valvalval'
#         resp = base.write_key(data_struct['uuid'], key, val)
#         assert resp[key] == val

# def test_job_write_key_fail(mongodb_settings):
#     base = PipelineJobStore(mongodb_settings)
#     for data_struct in pipelinejob.get_jobs():
#         key = 'pipeline_uuid'
#         val = '1234567890'
#         with pytest.raises(datacatalog.linkedstores.basestore.exceptions.CatalogError):
#             base.write_key(data_struct['uuid'], key, val)

# def test_job_soft_delete(mongodb_settings):
#     base = PipelineJobStore(mongodb_settings)
#     for data_struct in pipelinejob.get_jobs():
#         resp = base.delete_document(data_struct['uuid'])
#         assert resp['_visible'] is False

def test_job_agaveclient(mongodb_settings, agave):
    base = PipelineJobStore(
        mongodb_settings, agave=agave)
    assert getattr(base, '_helper') is not None

@longrun
def test_job_list_job_dir(mongodb_settings, agave):
    # The listed path is set up for test_agavehelpers and the job_uuid is the
    # from data/tests/pipelinejob/tacbobot.json
    job_uuid = '107b93f3-1eae-5e79-8a18-0a480f8aa3a5'
    base = PipelineJobStore(
        mongodb_settings, agave=agave)
    dirlist = base.list_job_archive_path(job_uuid, recurse=True)
    assert '/sample/tacc-cloud/agavehelpers/upload/transcriptic/hello.txt' in dirlist

@delete
def test_job_delete(mongodb_settings):
    base = PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_jobs():
        resp = base.delete_document(data_struct['uuid'], soft=False)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
