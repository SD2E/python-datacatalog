import pytest
from .fixtures import *

def pytest_addoption(parser):
    parser.addoption('--bootstrap', action='store_true', dest='bootstrap',
                     default=False, help='Run bootsrapping tasks and tests')
    parser.addoption('--delete', action='store_true', dest='delete',
                     default=False, help='Run tests that delete database entries')
    parser.addoption('--longrun', action='store_true', dest='longrun',
                     default=False, help='Run tests that might take a long time')
    parser.addoption('--networked', action='store_true', dest='networked',
                     default=False, help='Run tests that require external network access')
    parser.addoption('--smoketest', action='store_true', dest='smoketest',
                     default=False, help='Run developer smoktests')


def pytest_runtest_setup(item):
    if 'bootstrap' in item.keywords and not item.config.getvalue('bootstrap'):
        pytest.skip('needs --bootstrap option to run')
    if 'delete' in item.keywords and not item.config.getvalue('delete'):
        pytest.skip('needs --delete option to run')
    if 'longrun' in item.keywords and not item.config.getvalue('longrun'):
        pytest.skip('needs --longrun option to run')
    if 'networked' in item.keywords and not item.config.getvalue('networked'):
        pytest.skip('needs --networked option to run')
    if 'smoketest' in item.keywords and not item.config.getvalue('smoketest'):
        pytest.skip('needs --smoketest option to run')
