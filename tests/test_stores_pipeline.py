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
from data import pipeline

sys.path.insert(0, '/')
import datacatalog

def test_pipe_db(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)

def test_pipe_db_list_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    assert base.db.list_collection_names() is not None

def test_pipe_schema(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_pipe_name(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    assert base.name == 'pipelines'

def test_pipe_uuid_tytpe(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    assert base.get_uuid_type() == 'pipeline'

def test_pipe_write(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    for data_struct in pipeline.get_files():
        resp = base.add_update_document(data_struct['data'])
        assert resp['uuid'] == data_struct['uuid']

def test_pipe_write_update(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    for data_struct in pipeline.get_files():
        resp = base.add_update_document(data_struct['data'])
        assert resp['uuid'] == data_struct['uuid']

def test_pipe_write_key_ok(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    for data_struct in pipeline.get_files():
        key = 'keykeykey'
        val = 'valvalval'
        resp = base.write_key(data_struct['uuid'], key, val)
        assert resp[key] == val

def test_pipe_write_key_fail(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    for data_struct in pipeline.get_files():
        key = 'components'
        val = ['val', 'val', 'val']
        with pytest.raises(datacatalog.linkedstores.basestore.exceptions.CatalogError):
            base.write_key(data_struct['uuid'], key, val)

def test_pipe_soft_delete(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    for data_struct in pipeline.get_files():
        resp = base.delete_document(data_struct['uuid'])
        assert resp['_visible'] is False

def test_pipe_delete(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    for data_struct in pipeline.get_files():
        resp = base.delete_document(data_struct['uuid'], soft=False)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
