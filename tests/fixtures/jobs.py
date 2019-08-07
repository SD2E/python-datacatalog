import pytest
from datacatalog.identifiers import random_string
from datacatalog.managers.pipelinejobs import (
    ManagedPipelineJob, ManagedPipelineJobInstance, ManagedPipelineJobError)

__all__ = ['random_dir_name', 'list_job_uuid',
           'job_data', 'client_w_param', 'instanced_client_w_param',
           'client_w_param_data', 'client_w_archive_path',
           'client_w_sample_archive_path', 'instance_w_sample_archive_path',
           'pipeline_uuid', 'config_base', 'config_job_manager',
           'config_pipeline_manager', 'config_job_indexer',
           'pipelinejobs_config', 'job_index_filters']

@pytest.fixture(scope='session')
def random_dir_name():
    return random_string(32)

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
        }
    }
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
def client_w_sample_archive_path(mongodb_settings, pipelinejobs_config,
                                 agave, pipeline_uuid, admin_token):
    mpj = ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                             agave=agave, archive_path='/sample/tacc-cloud',
                             experiment_id='experiment.tacc.10001',
                             archive_patterns=[{'patterns': ['.json$'], 'level': '2'}],
                             product_patterns=[{'patterns': ['.json$'], 'derived_using': ['1092d775-0f7c-5b4d-970f-e739711d5f36', 'modified_ecoli_MG1655_refFlat_txt-0-1-0'], 'derived_from': ['105fb204-530b-5915-9fd6-caf88ca9ad8a', '1058868c-340e-5d8c-b66e-9739cbcf8d36', './672.png', 'agave://data-sd2e-community/sample/tacc-cloud/dawnofman.jpg']}])
    return mpj

@pytest.fixture(scope='session')
def client_w_sample_archive_path_missed_ref(mongodb_settings,
                                            pipelinejobs_config, agave,
                                            pipeline_uuid,
                                            admin_token):
    mpj = ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                             agave=agave, archive_path='/sample/tacc-cloud',
                             experiment_id='experiment.tacc.10001',
                             archive_patterns=[{'patterns': ['.json$'], 'level': '2'}],
                             product_patterns=[{'patterns': ['.json$'], 'derived_using': ['1092d775-0f7c-5b4d-970f-e739711d5f36', 'modified_ecoli_MG1655_refFlat_txt-0-1-0'], 'derived_from': ['105fb204-530b-5915-9fd6-caf88ca9ad8a', '1058868c-340e-5d8c-b66e-9739cbcf8d36', './672.png', 'agave://data-sd2e-community/sample/tacc-cloud/dawnofman.jpg']}])

    def initjob():
        mpj.setup()
        mpj.run(token=admin_token)
        mpj.finish(token=admin_token)
        return mpj

    job = None
    try:
        job = initjob()
    except ManagedPipelineJobError:
        mpj.reset(token=admin_token, no_clear_path=True, permissive=True)
        job = initjob()

    # print('MPJ.UUID', job.uuid)
    return job

@pytest.fixture(scope='session')
def instance_w_sample_archive_path(client_w_sample_archive_path, mongodb_settings, agave):
    c = client_w_sample_archive_path.setup()
    return ManagedPipelineJobInstance(mongodb_settings, c.uuid, agave=agave)

@pytest.fixture(scope='session')
def pipeline_uuid():
    """Resolves to the tacobot test pipeline
    """
    return '10650844-1baa-55c5-a481-5e945b19c065'

@pytest.fixture(scope='session')
def config_base():
    config_dict = {}
    return config_dict

@pytest.fixture(scope='session')
def config_job_manager(pipeline_uuid, actor_id, nonce_id):
    config_dict = {'job_manager_id': actor_id,
                   'job_manager_nonce': nonce_id,
                   'pipeline_uuid': pipeline_uuid}
    return config_dict

@pytest.fixture(scope='session')
def config_pipeline_manager(actor_id, nonce_id):
    config_dict = {'pipeline_manager_id': actor_id,
                   'pipeline_manager_nonce': nonce_id}
    return config_dict

@pytest.fixture(scope='session')
def config_job_indexer(actor_id, nonce_id):
    config_dict = {'job_indexer_id': actor_id,
                   'job_indexer_nonce': nonce_id}
    return config_dict

@pytest.fixture(scope='session')
def pipelinejobs_config(config_base, config_job_manager, config_job_indexer):
    config_dict = {**config_base, **config_job_manager}
    config_dict = {**config_dict, **config_job_indexer}
    return config_dict


@pytest.fixture(scope='session')
def job_index_filters():
    archive_patterns = [{'patterns': ['.png$'], 'level': 'User'}]
    product_patterns = [{'patterns': ['ansible.png$'],
                        'derived_using': [],
                        'derived_from': ['./biofab/blebob.jpg']}]
    filters = list()
    filters.extend(archive_patterns)
    filters.extend(product_patterns)
    return filters
