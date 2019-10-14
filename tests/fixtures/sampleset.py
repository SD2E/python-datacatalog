import pytest
from datacatalog.managers import sampleset

__all__ = ['sampleset_processor']

@pytest.fixture(scope='session')
def sampleset_processor(mongodb_settings):
    return sampleset.SampleSetProcessor(mongodb_settings)
