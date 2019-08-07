import os
import pytest
from tempfile import mkdtemp

__all__ = ['temp_dir']

@pytest.fixture(scope='session')
def temp_dir():
    """Alternative to pytest's temporary directory function
    """
    return mkdtemp(prefix='datacatalog-', suffix='-tests')
