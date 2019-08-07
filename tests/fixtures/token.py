import pytest
import os
import random
from datacatalog import tokens
from datacatalog.identifiers import random_string

__all__ = ['admin_key', 'admin_token',
           'crypto_salt',
           'generated_admin_key', 'generated_admin_secret',
           'env_override_admin_key', 'env_override_admin_secret',
           'short_token_ttl']

@pytest.fixture(scope='function')
def admin_key():
    """Returns the current value of the admin token issuance key
    """
    return tokens.admin.get_admin_key()

@pytest.fixture(scope='function')
def admin_token(admin_key):
    """Returns the current administrative token
    """
    return tokens.admin.get_admin_token(admin_key)

@pytest.fixture(scope='function')
def crypto_salt():
    """Generates a good quality cryptographic salt
    """
    return tokens.generate_salt()

@pytest.fixture(scope='function')
def generated_admin_key():
    """Generates a plaintext random token key
    """
    return random_string()

@pytest.fixture(scope='function')
def generated_admin_secret():
    """Generates a plaintext random token secret
    """
    return random_string()

@pytest.fixture(scope='function')
def env_override_admin_key(monkeypatch, generated_admin_key):
    """Override Data Catalog admin key using os.environ
    """
    gen_key = generated_admin_key
    monkeypatch.setenv('CATALOG_ADMIN_TOKEN_KEY', gen_key)
    return gen_key

@pytest.fixture(scope='function')
def env_override_admin_secret(monkeypatch, generated_admin_secret):
    """Override Data Catalog admin secret using os.environ
    """
    gen_key = generated_admin_secret
    monkeypatch.setenv('CATALOG_ADMIN_TOKEN_SECRET', gen_key)
    return gen_key

@pytest.fixture(scope='function')
def short_token_ttl(monkeypatch):
    """Overrides the admin token TTL using os.environ
    """
    ttl = int(random.random() * 3) + 1
    monkeypatch.setenv('CATALOG_ADMIN_TOKEN_LIFETIME', str(ttl))
    return ttl

