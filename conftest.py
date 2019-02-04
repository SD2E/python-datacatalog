import pytest
from datacatalog.identifiers import abaco, interestinganimal, typeduuid


def pytest_addoption(parser):
    parser.addoption('--longrun', action='store_true', dest="longrun",
                     default=False, help="Enable tests that might take a long time")
    parser.addoption('--networked', action='store_true', dest="networked",
                     default=False, help="Enable tests that require external network access")
    parser.addoption('--delete', action='store_true', dest="delete",
                     default=False, help="Enable tests that delete database entries")
    parser.addoption('--bootstrap', action='store_true', dest="bootstrap",
                     default=False, help="Run bootstrapping tests for development environment")

@pytest.fixture(scope='session')
def nonce():
    return abaco.nonceid.generate()

@pytest.fixture(scope='session')
def pipeline_uuid():
    """Resolves to the tacobot test pipeline"""
    return '10650844-1baa-55c5-a481-5e945b19c065'

@pytest.fixture(scope='session')
def manager_id():
    return abaco.actorid.generate()

@pytest.fixture(scope='session')
def agave_app_id():
    return 'zoomania-0.1.1'

@pytest.fixture(scope='session')
def agave_job_id():
    return '6583653933928541720-242ac11b-0001-007'

@pytest.fixture(scope='session')
def actor_id():
    return abaco.actorid.generate()

@pytest.fixture(scope='session')
def exec_id():
    return abaco.execid.generate()

@pytest.fixture(scope='session')
def session():
    return interestinganimal.generate(timestamp=False)

@pytest.fixture(scope='session')
def config_base():
    config_dict = {}
    return config_dict

@pytest.fixture(scope='session')
def config_job_manager(pipeline_uuid):
    config_dict = {'job_manager_id': abaco.actorid.generate(),
                   'job_manager_nonce': abaco.nonceid.generate(),
                   'pipeline_uuid': pipeline_uuid}
    return config_dict

@pytest.fixture(scope='session')
def config_pipeline_manager():
    config_dict = {'pipeline_manager_id': abaco.actorid.generate(),
                   'pipeline_manager_nonce': abaco.nonceid.generate()}
    return config_dict

@pytest.fixture(scope='session')
def config_job_indexer():
    config_dict = {'job_indexer_id': abaco.actorid.generate(),
                   'job_indexer_nonce': abaco.nonceid.generate()}
    return config_dict

@pytest.fixture(scope='session')
def pipelinejobs_config(config_base, config_job_manager, config_job_indexer):
    config_dict = {**config_base, **config_job_manager}
    config_dict = {**config_dict, **config_job_indexer}
    return config_dict
