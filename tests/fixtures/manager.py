import pytest
from datacatalog import managers

__all__ = ['catalog_manager']

@pytest.fixture(scope='session')
def catalog_manager(mongodb_settings):
    """Returns a bare-bones CatalogManager instance
    """
    return managers.catalog.CatalogManager(mongodb_settings)
