import pytest

__all__ = ['env_localonly', 'env_debug', 'env_make_tests']

@pytest.fixture(scope='function')
def env_localonly(monkeypatch):
    """Overrides the debug variable LOCALONLY which is used in debugging Actors
    """
    monkeypatch.setenv('LOCALONLY', '1')
    return True

@pytest.fixture(scope='function')
def env_debug(monkeypatch):
    """Overrides the DEBUG variable which is read by the settings module
    """
    monkeypatch.setenv('DEBUG', 'true')
    return True

@pytest.fixture(scope='function')
def env_make_tests(monkeypatch):
    """Overrides the MAKETESTS variable which is used to configure scripts behavior
    """
    monkeypatch.setenv('MAKETESTS', '1')
    return True
