import pytest
from datacatalog.identifiers import abaco

__all__ = ['nonce_id', 'manager_actor_id',
           'actor_id', 'exec_id', 'worker_id']

@pytest.fixture(scope='session')
def nonce_id():
    return abaco.nonceid.generate()

@pytest.fixture(scope='session')
def manager_actor_id():
    return abaco.actorid.generate()

@pytest.fixture(scope='session')
def actor_id():
    return abaco.actorid.generate()

@pytest.fixture(scope='session')
def exec_id():
    return abaco.execid.generate()

@pytest.fixture(scope='session')
def worker_id():
    return abaco.execid.generate()
