import pytest
import os

from datacatalog.managers.pipelinejobs import ReactorManagedPipelineJob
from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance
from datacatalog.identifiers import abaco, interestinganimal, typeduuid
from .data import pipelinejobs

def test_rxpipejob_init_store_list(reactor_job_client):
    """Verifies that ReactorManagedPipelineJob can get through ``init()``
    """
    assert list(reactor_job_client.stores.keys()) != list()

def test_rxpipejob_init_archive_path_instanced(reactor_job_client):
    """Exercises ``instanced=True`` which causes archive path to be
    collision-proof
    """
    assert reactor_job_client.archive_path.startswith('/products/v2')
    assert '/106' in reactor_job_client.archive_path
    assert not reactor_job_client.archive_path.endswith('Z')

