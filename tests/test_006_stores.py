import os
import pytest
import sys
import yaml
import json
from agavepy.agave import Agave
from pprint import pprint
from . import longrun, delete
from .fixtures import agave, credentials

from datacatalog.stores import StorageSystem, ManagedStoreError


CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.mark.parametrize("system_id, abaco_dir, jupyter_dir", [
    ('data-sd2e-community',
        '/work/projects/SD2E-Community/prod/data',
            '/user/{User}/tree/sd2e-community'),
    ('data-tacc-work-sd2eadm',
        '/work/05201/sd2eadm',
            '/user/sd2eadm/tree/tacc-work'),
    ('data-projects-biocon',
        '/work/projects/DARPA-SD2-Partners/biocon',
            '/user/{User}/tree/sd2e-partners/biocon'),
    ('data-sd2e-projects.sd2e-project-10',
        '/work/projects/SD2E-Community/prod/projects/sd2e-project-10',
            '/user/{User}/tree/sd2e-projects/sd2e-project-10'),
    ('data-sd2e-projects.sd2e-project-21',
        '/work/projects/SD2E-Community/prod/projects/sd2e-project-21',
            '/user/{User}/tree/sd2e-projects/sd2e-project-21')])
def test_storage_system_base_dirs(agave, system_id, abaco_dir, jupyter_dir):
    """General test for system mappings"""
    store = StorageSystem(system_id, agave=agave)
    assert store.abaco_dir == abaco_dir
    assert store.jupyter_dir == jupyter_dir

@pytest.mark.parametrize("system_id", [('data-tacc-home-sd2eadm'), ('data-project-biocon')])
def test_storage_system_raises(agave, system_id):
    """Non-existent systems fail"""
    with pytest.raises(ManagedStoreError):
        store = StorageSystem(system_id, agave=agave)

@pytest.mark.parametrize("system_id", [('data-sd2e-projects-users')])
def test_storage_system_public_no_jupyter(agave, system_id):
    """Agave public system not exposed via Jupyter"""
    with pytest.raises(ManagedStoreError):
        store = StorageSystem(system_id, agave=agave).jupyter_dir
