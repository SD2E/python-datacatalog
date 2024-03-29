import os
import pytest
import json
from pprint import pprint

from datacatalog.linkedstores.pipeline import PipelineStore, SerializedPipeline
from .data import pipeline

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_pipe_db(mongodb_settings):
    base = PipelineStore(mongodb_settings)
    assert base is not None

def test_pipe_schema(mongodb_settings):
    base = PipelineStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_pipe_name(mongodb_settings):
    base = PipelineStore(mongodb_settings)
    assert base.name == 'pipelines'

def test_pipe_uuid_tytpe(mongodb_settings):
    base = PipelineStore(mongodb_settings)
    assert base.get_uuid_type() == 'pipeline'

def test_pipe_serialized_classify_validate():
    for ctype, component in pipeline.COMPONENTS:
        assert SerializedPipeline.classify_component(component) == ctype

def test_pipe_disk_load_classify_components():
    for filename, pipe_uuid, noop in pipeline.CASES:
        doc = json.load(open(os.path.join(pipeline.DATADIR, filename), 'r'))
        for component in doc.get('components'):
            kind = SerializedPipeline.classify_component(component)
            try:
                assert kind is not None
            except Exception:
                print('Failed To Classify Component')
                pprint(component)
                raise

def test_pipe_disk_load(mongodb_settings):
    base = PipelineStore(mongodb_settings)
    for filename, pipe_uuid, noop in pipeline.CASES:
        doc = json.load(open(os.path.join(pipeline.DATADIR, filename), 'r'))
        resp = base.add_update_document(doc, strategy='replace')
        try:
            assert resp['uuid'] == pipe_uuid
        except Exception:
            print('UUID for Pipeline {} should be {}'.format(filename, resp['uuid']))
            raise

@pytest.mark.delete
def test_pipe_disk_delete(mongodb_settings):
    base = PipelineStore(mongodb_settings)
    for filename, pipe_uuid, noop in pipeline.CASES:
        # Note: Use hard delete here!
        resp = base.delete_document(pipe_uuid, force=True)
        try:
            assert resp.raw_result == {'n': 1, 'ok': 1.0}
        except Exception:
            print('Failed to delete Pipeline ({}) w UUID'.format(filename, resp['uuid']))
            raise
