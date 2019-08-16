import pytest

__all__ = ['challenge_problem_id',
           'experiment_design_id',
           'experiment_id',
           'sample_id']

@pytest.fixture(scope='session')
def challenge_problem_id():
    return 'PIPELINE_AUTOMATION'

@pytest.fixture(scope='session')
def experiment_design_id():
    return 'Pipeline-Automation'

@pytest.fixture(scope='session')
def experiment_id():
    return 'experiment.ginkgo.10001'

@pytest.fixture(scope='session')
def sample_id():
    return 'sample.uw_biofab.143209/H1'
