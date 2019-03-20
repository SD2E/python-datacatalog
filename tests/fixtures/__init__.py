import pytest
from datacatalog import tokens

from .agave import agave, credentials, settings
from .mongodb import mongodb_settings, mongodb_authn

@pytest.fixture(scope='session')
def admin_key():
    return tokens.admin.get_admin_key()

@pytest.fixture(scope='session')
def admin_token(admin_key):
    return tokens.admin.get_admin_token(admin_key)
