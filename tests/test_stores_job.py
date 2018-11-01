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
from data import pipelinejob

sys.path.insert(0, '/')
import datacatalog

def test_job_db(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)

def test_job_db_list_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    assert base.db.list_collection_names() is not None

def test_job_schema(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_job_name(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    assert base.name == 'jobs'

def test_job_uuid_tytpe(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    assert base.get_uuid_type() == 'pipelinejob'

def test_job_create(mongodb_settings, monkeypatch):
    monkeypatch.setenv('LOCALONLY', '1')
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_jobs():
        resp = base.create(data_struct['data'])
        assert resp['uuid'] == data_struct['uuid']

def test_handle_event(mongodb_settings, monkeypatch):
    monkeypatch.setenv('LOCALONLY', '1')
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_events():
        resp = base.handle(data_struct['data'])
        assert resp['uuid'] == data_struct['uuid']

def test_job_write_key_ok(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_jobs():
        key = 'keykeykey'
        val = 'valvalval'
        resp = base.write_key(data_struct['uuid'], key, val)
        assert resp[key] == val

def test_job_write_key_fail(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_jobs():
        key = 'actor_id'
        val = ['val', 'val', 'val']
        with pytest.raises(datacatalog.linkedstores.basestore.exceptions.CatalogError):
            base.write_key(data_struct['uuid'], key, val)

def test_job_soft_delete(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_jobs():
        resp = base.delete_document(data_struct['uuid'])
        assert resp['_visible'] is False

def test_job_delete(mongodb_settings):
    base = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    for data_struct in pipelinejob.get_jobs():
        resp = base.delete_document(data_struct['uuid'], soft=False)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}