import os
import pytest

__all__ = ['pjso_cache_dir']

@pytest.fixture(scope='function')
def pjso_cache_dir(monkeypatch, temp_dir):
    """Overrides the cache directory used to instantiate objects from JSONschema
    """
    monkeypatch.setenv('CATALOG_PJS_CACHE_DIR', temp_dir)
    return temp_dir

