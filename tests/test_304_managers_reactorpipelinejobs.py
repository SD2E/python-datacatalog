import os
import pytest
import sys
import yaml
import json
from attrdict import AttrDict
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
from .fixtures.agave import agave, credentials
import datacatalog
import transitions
from datacatalog.identifiers import abaco, interestinganimal, typeduuid
from .data import pipelinejobs

from datacatalog.managers.pipelinejobs import ReactorManagedPipelineJob
from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.fixture(scope='session')
def experiment_id():
    return 'experiment.ginkgo.10001'

@pytest.fixture(scope='session')
def sample_id():
    return 'sample.uw_biofab.143209/H1'

@pytest.fixture(scope='session')
def rx_settings(mongodb_settings, pipelinejobs_config):
    sets = dict()
    sets['pipelines'] = pipelinejobs_config
    sets['mongodb'] = mongodb_settings
    return AttrDict(sets)

@pytest.fixture(scope='session')
def reactor(rx_settings, agave, actor_id, exec_id, session):
    '''Return a functional Agave client'''
    rx = dict()
    rx['settings'] = rx_settings
    rx['uid'] = actor_id
    rx['execid'] = exec_id
    rx['nickname'] = session
    rx['client'] = agave
    return AttrDict(rx)

@pytest.fixture(scope='session')
def rx_client(reactor, experiment_id):
    return ReactorManagedPipelineJob(
        reactor,
        experiment_id=experiment_id,
        instanced=False)

def test_rxpipejob_init_store_list(rx_client):
    """Smoke test: Can ReactorManagedPipelineJob get through ``init()``
    """
    assert list(rx_client.stores.keys()) != list()

def test_rxpipejob_init_archive_path_instanced(rx_client):
    """Exercises ``instanced=True`` which causes archive path to be
    collision-proof
    """
    assert rx_client.archive_path.startswith('/products/v2')
    assert '/106' in rx_client.archive_path
    assert not rx_client.archive_path.endswith('Z')

