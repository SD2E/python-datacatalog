import os
import pytest
import sys
import yaml
import json
import time
from pprint import pprint
from . import longrun, delete
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.fixture(scope='session')
def admin_key():
    return datacatalog.tokens.admin.get_admin_key()

@pytest.fixture(scope='session')
def salt():
    return datacatalog.tokens.generate_salt()

def test_get_token(salt):
    token = datacatalog.tokens.get_token(salt, 'arg1', 'arg2')
    assert isinstance(token, str)

def test_validate_token(salt):
    token = datacatalog.tokens.get_token(salt, 'arg1', 'arg2')
    assert datacatalog.tokens.validate_token(token, salt, 'arg1', 'arg2') is True

def test_validate_token_false_permissive(salt):
    token = datacatalog.tokens.get_token(salt, 'arg1', 'arg2')
    assert datacatalog.tokens.validate_token(token, salt, 'arg1', 'arg3') is False

def test_validate_token_false(salt):
    token = datacatalog.tokens.get_token(salt, 'arg1', 'arg2')
    with pytest.raises(ValueError):
        datacatalog.tokens.validate_token(token, salt, 'arg1', 'arg3', permissive=False)

def test_validate_token_passthru(salt, admin_key):
    token = datacatalog.tokens.get_admin_token(admin_key)
    assert datacatalog.tokens.validate_token(token, salt) is True

# def test_validate_token_admin_override(salt):
#     token = datacatalog.tokens.__get_admin_tokens()[0]
#     assert datacatalog.tokens.validate_token(token, salt, permissive=False) is True

def test_validate_admin_token_valid(salt, admin_key):
    token = datacatalog.tokens.get_admin_token(admin_key)
    assert datacatalog.tokens.validate_admin_token(token, admin_key, permissive=False) is True

def test_validate_admin_token_env_key_valid(monkeypatch):
    monkeypatch.setenv('CATALOG_ADMIN_TOKEN_KEY', 'sK3thEPHwuRTUkCwHzU7PBSQNJp5jaeP')
    api_key = datacatalog.tokens.admin.get_admin_key()
    token = datacatalog.tokens.get_admin_token(api_key)
    assert datacatalog.tokens.validate_admin_token(token, api_key, permissive=False) is True

def test_validate_admin_token_env_secret_valid(monkeypatch, admin_key):
    monkeypatch.setenv('CATALOG_ADMIN_TOKEN_SECRET', 'YThRMxBcYpu7uFe82YC7VCKBUd5XUmfV')
    token = datacatalog.tokens.get_admin_token(admin_key)
    assert datacatalog.tokens.validate_admin_token(token, admin_key, permissive=False) is True

def test_validate_admin_token_passed_valid(salt, admin_key):
    token = datacatalog.tokens.get_admin_token(admin_key)
    assert datacatalog.tokens.validate_admin_token(token, admin_key, permissive=False) is True

def test_validate_admin_token_notpassed_fail(salt, admin_key):
    # Turns off global debug mode
    token = datacatalog.tokens.get_admin_token(admin_key)
    assert token is not None

def test_validate_admin_token_passed_invalid(salt):
    token = 'gmw6jqb3r5ts1b2y'
    with pytest.raises(ValueError):
        datacatalog.tokens.validate_admin_token(token, permissive=False) is True

@longrun
def test_validate_admin_token_timeout(salt, monkeypatch, admin_key):
    tok_lifetime = "2"
    monkeypatch.setenv('CATALOG_ADMIN_TOKEN_LIFETIME', tok_lifetime)
#     assert datacatalog.tokens.get_admin_lifetime() == int(tok_lifetime)
    token = datacatalog.tokens.get_admin_token(key=admin_key)
    token_life = datacatalog.tokens.get_admin_lifetime()
    assert datacatalog.tokens.validate_admin_token(token, key=admin_key, permissive=False) is True
    time.sleep(int(token_life) * 1.1)
    with pytest.raises(ValueError):
        datacatalog.tokens.validate_admin_token(token, key=admin_key, permissive=False) is True
