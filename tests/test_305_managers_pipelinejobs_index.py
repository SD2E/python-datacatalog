import os
import pytest
import sys
import yaml
import json
import inspect
import warnings
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
from .fixtures.agave import agave, credentials
import datacatalog
import traceback
import transitions
from datacatalog.identifiers import abaco, interestinganimal, typeduuid
from .data import pipelinejobs

from datacatalog.managers.pipelinejobs import ManagedPipelineJob
from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.fixture(scope='session')
def admin_key():
    return datacatalog.tokens.admin.get_admin_key()

@pytest.fixture(scope='session')
def admin_token(admin_key):
    return datacatalog.tokens.admin.get_admin_token(admin_key)

@pytest.fixture(scope='session')
def experiment_id():
    return 'experiment.ginkgo.10001'

@pytest.fixture(scope='session')
def sample_id():
    return 'sample.uw_biofab.143209/H1'

@pytest.fixture(scope='session')
def list_job_uuid():
    return '107b93f3-1eae-5e79-8a18-0a480f8aa3a5'

@pytest.fixture(scope='session')
def job_data():
    data_obj = {
        'inputs': {
            'file1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
            'ref1': 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_WT/MG1655_WT.fa.ann'},
        'parameters': {
            'param2': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    }}
    return data_obj

@pytest.fixture(scope='session')
def client_w_param(mongodb_settings, pipelinejobs_config,
                   agave, pipeline_uuid, experiment_id):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave, experiment_id=experiment_id)

@pytest.fixture(scope='session')
def instanced_client_w_param(mongodb_settings, pipelinejobs_config,
                             agave, pipeline_uuid, experiment_id):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave, experiment_id=experiment_id,
                              instanced=True)

@pytest.fixture(scope='session')
def client_w_param_data(mongodb_settings, pipelinejobs_config,
                        agave, pipeline_uuid, experiment_id, job_data):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave,
                              experiment_id=experiment_id,
                              data=job_data)

@pytest.fixture(scope='session')
def client_w_archive_path(mongodb_settings, pipelinejobs_config,
                          agave, pipeline_uuid):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave, archive_path='/products/v2/test123')

@pytest.fixture(scope='session')
def defined_filters():
    archive_patterns=[{'patterns': ['.png$'], 'level': 'User'}]
    product_patterns=[{'patterns': ['ansible.png$'], 'derived_using': [], 'derived_from': ['./biofab/blebob.jpg']}]
    filters = list()
    filters.extend(archive_patterns)
    filters.extend(product_patterns)
    return filters

@longrun
def test_pipesinst_index_explicit_filters(mongodb_settings, agave, defined_filters):
    """Indexing with explicit filters => job.archive_path x specified filters
    """
    # This job is generated in the database by test_109#test_job_create
    # Its archive_patterns = ['ansible.png']
    job_uuid = '107b93f3-1eae-5e79-8a18-0a480f8aa3a5'
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
    indexed = base.index(filters=defined_filters, transition=False)
    # This is a trick. We index 'ansible.png' twice!
    assert len(indexed) == 1

@longrun
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


