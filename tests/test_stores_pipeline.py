import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
from .data import pipeline

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

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

def test_pipe_write_create(mongodb_settings):
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

@delete
def test_pipe_delete(mongodb_settings):
    base = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_settings)
    for data_struct in pipeline.get_files():
        resp = base.delete_document(data_struct['uuid'], soft=False)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}

def test_pipe_serialized_classify_validate():
    from datacatalog.linkedstores.pipeline.serializer import SerializedPipeline
    for ctype, component in pipeline.COMPONENTS:
        pprint(component)
        assert SerializedPipeline.classify_component(component) == ctype


def test_pipe_serialized_classify_examples():
    from datacatalog.linkedstores.pipeline.serializer import SerializedPipeline
    for data_struct in pipeline.get_files():
        for component in data_struct['data']['components']:
            kind = SerializedPipeline.classify_component(component)
            assert kind is not None
