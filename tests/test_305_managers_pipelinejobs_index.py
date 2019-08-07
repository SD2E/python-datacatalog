import pytest
import os

from datacatalog.managers.pipelinejobs import (
    ManagedPipelineJob, ManagedPipelineJobInstance)
from datacatalog.identifiers import (abaco, interestinganimal, typeduuid)
from .data import pipelinejobs

@pytest.mark.longrun
def test_pipesinst_index_explicit_filters(mongodb_settings, agave, job_index_filters):
    """Indexing with explicit filters => job.archive_path x specified filters
    """
    # This job is generated in the database by test_109#test_job_create
    # Its archive_patterns = ['ansible.png']
    job_uuid = '107b93f3-1eae-5e79-8a18-0a480f8aa3a5'
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
    indexed = base.index(filters=job_index_filters, transition=False)
    # This is a trick. We index 'ansible.png' twice!
    assert len(indexed) == 1

@pytest.mark.longrun
def test_pipesinst_index_no_filters_w_defaults(mongodb_settings, agave):
    """Indexing with null filters => job.archive_path x default archive_patterns
    """
    # This job is generated in the database by test_109#test_job_create
    # Its archive_patterns = ['ansible.png']
    job_uuid = '107b93f3-1eae-5e79-8a18-0a480f8aa3a5'
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
    listed = base.index()
    # should only match 'ansible.png'
    assert len(listed) == 1

