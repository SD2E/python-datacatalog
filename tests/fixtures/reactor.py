import pytest
from attrdict import AttrDict
from datacatalog.managers.pipelinejobs import ReactorManagedPipelineJob

__all__ = ['reactor_settings', 'reactor_object', 'reactor_job_client']

@pytest.fixture(scope='session')
def reactor_settings(mongodb_settings, pipelinejobs_config):
    """Emulates dict passed in from ``config.yml
    """
    sets = dict()
    sets['pipelines'] = pipelinejobs_config
    sets['mongodb'] = mongodb_settings
    return AttrDict(sets)

@pytest.fixture(scope='session')
def reactor_object(rx_settings, agave, actor_id, exec_id, session):
    """Return a functional Agave client
    """
    rx = dict()
    rx['settings'] = rx_settings
    rx['uid'] = actor_id
    rx['execid'] = exec_id
    rx['nickname'] = session
    rx['client'] = agave
    return AttrDict(rx)

@pytest.fixture(scope='session')
def reactor_job_client(reactor, experiment_id):
    """Returns a PipelineJob client using the Reactors API
    """
    return ReactorManagedPipelineJob(
        reactor, experiment_id=experiment_id, instanced=False)

