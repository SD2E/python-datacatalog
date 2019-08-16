import pytest
from datacatalog.identifiers import interestinganimal

__all__ = ['session', 'timestamped_session']

@pytest.fixture(scope='session')
def session():
    return interestinganimal.generate(timestamp=False)

@pytest.fixture(scope='session')
def timestamped_session():
    return interestinganimal.generate(timestamp=True)
