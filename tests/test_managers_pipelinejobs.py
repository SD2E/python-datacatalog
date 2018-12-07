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
    return '1064aaf1-459c-5e42-820d-b822aa4b3990'

@pytest.fixture(scope='session')
def experiment_id():
    return 'experiment.uw_biofab.17987'

@pytest.fixture(scope='session')
def sample_id():
    return 'sample.uw_biofab.143209/H1'

@pytest.fixture(scope='session')
def manager_id():
    return datacatalog.identifiers.abaco.actorid.generate()

@pytest.fixture(scope='session')
def nonce():
    return 'TACC_' + datacatalog.identifiers.abaco.actorid.generate()

@pytest.fixture(scope='session')
def actor_id():
    return datacatalog.identifiers.abaco.actorid.generate()

@pytest.fixture(scope='session')
def exec_id():
    return datacatalog.identifiers.abaco.execid.generate()

@pytest.fixture(scope='session')
def session():
    return datacatalog.identifiers.interestinganimal.generate(timestamp=False)

@pytest.fixture(scope='session')
def agave_app_id():
    return 'zoomania-0.1.1'

@pytest.fixture(scope='session')
def agave_job_id():
    return '6583653933928541720-242ac11b-0001-007'

def test_pipesjob_get_stores(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    assert list(base.stores.keys()) != list()

def test_pipesjob_setup(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    assert base.pipeline_uuid == pipeline_uuid
    assert 'example_data' in base.data
    assert base.archive_path.startswith('/products')

def test_pipesjob_setup_instanced(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, instanced=True)
    base.setup(data={'example_data': 'datadata'})
    assert base.archive_path.endswith('Z')

def test_pipesjob_setup_not_instanced(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, instanced=False)
    base.setup(data={'example_data': 'datadata'})
    assert not base.archive_path.endswith('Z')

def test_pipesjob_callback(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    assert base.callback.startswith('https://')

def test_pipesjob_run(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})

def test_pipesjob_update(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})

def test_pipesjob_fail(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})
    base.fail(data={'this_data': 'is from a fail event'})

def test_pipesjob_fail_fsm_enforce(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})
    base.fail(data={'this_data': 'is from a fail event'})
    with pytest.raises(transitions.core.MachineError):
        base.update(data={'this_data': 'is from an update event'})

def test_pipesjob_finish(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    base.update(data={'this_data': 'is from an update event'})
    base.finish(data={'this_data': 'is from a finish event'})

def test_pipesjob_no_finish_without_run(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
    base.setup(data={'example_data': 'datadata'})
    with pytest.raises(transitions.core.MachineError):
        base.finish(data={'this_data': 'is from a finish event'})

def test_pipesjob_mgr_params(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, actor_id, session):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=actor_id, session=session)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    assert base.session == session
    assert base.job['agent'].endswith(actor_id)

def test_pipesjob_task(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, actor_id, exec_id, session):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=actor_id, task=exec_id, session=session)
    base.setup(data={'example_data': 'datadata'})
    assert base.session == session
    assert base.job['task'].endswith(exec_id)

def test_pipesjob_agave_agent_task(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, agave_app_id, agave_job_id, session):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=agave_app_id, task=agave_job_id, session=session)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    assert base.job['agent'].endswith(agave_app_id)
    assert base.job['task'].endswith(agave_job_id)

def test_pipesjob_custom_archive_path(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, actor_id, session):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=actor_id, session=session, archive_path='/archives')
    base.setup(data={'example_data': 'datadata'})
    assert base.job['archive_path'] == '/archives'

@pytest.mark.parametrize("param,value,success", [('experiment_id', 'experiment.uw_biofab.17987', True),
                                                 ('sample_id', 'sample.uw_biofab.143209/H1', True),
                                                 ('measurement_id', 'measurement.uw_biofab.92242', True),
                                                 ('agent', '6e87V7aqrX646', False)])
def test_pipesjob_one_of_params(mongodb_settings, manager_id, nonce, param, value, success, pipeline_uuid):
    doc = {'pipeline_uuid': pipeline_uuid, param: value}
    if success is True:
        mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
        mjob.setup()
        assert mjob.pipeline_uuid == doc['pipeline_uuid']
    else:
        with pytest.raises(datacatalog.managers.pipelinejobs.store.ManagedPipelineJobError):
            mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
            mjob.setup()

@delete
def test_pipesjob_no_cancel_after_run(mongodb_settings, manager_id, nonce, pipeline_uuid):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid)
    base.setup(data={'example_data': 'datadata'})
    base.run(data={'this_data': 'is from the "run" event'})
    with pytest.raises(datacatalog.managers.pipelinejobs.ManagedPipelineJobError):
        base.cancel()

@delete
def test_pipesjob_cancel(mongodb_settings, manager_id, nonce, pipeline_uuid):
    base = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid)
    base.setup(data={'example_data': 'datadata'})
    base.cancel()

def test_pipesjob_create_jobs_kwargs(mongodb_settings, manager_id, nonce):
    for struct in pipelinejobs.get_jobs():
        doc = struct['data']
        # pprint(doc)
        if struct['valid'] is True:
            mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
            mjob.setup()
            assert mjob.uuid == struct['uuid']
        else:
            with pytest.raises(datacatalog.managers.pipelinejobs.store.ManagedPipelineJobError):
                mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
                mjob.setup()

@delete
def test_pipesjob_delete_jobs_kwargs(mongodb_settings, manager_id, nonce):
    for struct in pipelinejobs.get_jobs():
        doc = struct['data']
        if struct['valid'] is True:
            mjob = datacatalog.managers.pipelinejobs.ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
            mjob.setup()
            assert mjob.uuid == struct['uuid']
            mjob.cancel()
