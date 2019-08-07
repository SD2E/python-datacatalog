import pytest

__all__ = ['mock_tenant']

@pytest.fixture(scope='session')
def mock_tenant(monkeypatch):
    monkeypatch.setenv("CATALOG_DNS_DOMAIN", "salsa.club")
    monkeypatch.setenv("CATALOG_TACC_TENANT", "salsa.club")
    monkeypatch.setenv("CATALOG_TACC_API_SERVER'", "https://api.salsa.club")
    monkeypatch.setenv("CATALOG_TACC_MANAGER_ACCOUNT'", "salsita")
    monkeypatch.setenv("CATALOG_TACC_PROJECT_NAME'", "Salsalogic")
