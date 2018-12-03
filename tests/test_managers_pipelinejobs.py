import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
import transitions
from .data import pipelinejobs


CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.fixture(scope='session')
def pipeline_uuid():
    return '106c3276-b4b8-5f48-903d-722b22b1e021'

@pytest.fixture(scope='session')
def experiment_id():
    return 'experiment.uw_biofab.17987'

@pytest.fixture(scope='session')
def sample_id():
    return 'sample.uw_biofab.143209/H1'

@pytest.fixture(scope='session')
def actor_id():
    return datacatalog.identifiers.abacoid.generate()

@pytest.fixture(scope='session')
def session():
    return datacatalog.identifiers.interestinganimal.generate(timestamp=False)

def test_pipesjob_get_stores(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    assert list(base.stores.keys()) != list()

def test_pipesjob_setup(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    assert base.pipeline_uuid == pipeline_uuid
    assert 'example_data' in base.data
    assert base.archive_path.startswith('/products')

def test_pipesjob_run(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})

def test_pipesjob_update(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})

def test_pipesjob_fail(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})
    base.fail(data={'this_data': 'is from a fail event'})

def test_pipesjob_fail_fsm_enforce(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})
    base.fail(data={'this_data': 'is from a fail event'})
    with pytest.raises(transitions.core.MachineError):
        base.update(data={'this_data': 'is from an update event'})

def test_pipesjob_finish(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})
    base.finish(data={'this_data': 'is from a finish event'})

def test_pipesjob_no_finish_without_run(mongodb_settings, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    with pytest.raises(transitions.core.MachineError):
        base.finish(data={'this_data': 'is from a finish event'})

def test_pipesjob_mgr_params(mongodb_settings, pipeline_uuid, experiment_id, sample_id, actor_id, session):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, actor_id=actor_id, session=session)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    assert base.session == session
    assert base.job['actor_id'] == actor_id

@delete
def test_pipesjob_no_cancel_after_run(mongodb_settings, pipeline_uuid):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    with pytest.raises(datacatalog.managers.pipelinejobs.ManagedPipelineJobError):
        base.cancel()

@delete
def test_pipesjob_cancel(mongodb_settings, pipeline_uuid):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, pipeline_uuid=pipeline_uuid)
    base.setup(data={'example_data': 'datadata'})
    base.cancel()

def test_pipesjob_create_jobs_kwargs(mongodb_settings):
    for struct in pipelinejobs.get_jobs():
        doc = struct['data']
        if struct['valid'] is True:
            mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, **doc)
            mjob.setup()
            assert mjob.uuid == struct['uuid']
        else:
            with pytest.raises(datacatalog.managers.pipelinejobs.store.ManagedPipelineJobError):
                mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, **doc)
                mjob.setup()

@delete
def test_pipesjob_delete_jobs_kwargs(mongodb_settings):
    for struct in pipelinejobs.get_jobs():
        doc = struct['data']
        if struct['valid'] is True:
            mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, **doc)
            mjob.setup()
            assert mjob.uuid == struct['uuid']
            mjob.cancel()
