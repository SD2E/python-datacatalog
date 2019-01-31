import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)


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

def test_validate_token_admin_override(salt):
    token = datacatalog.tokens.get_admin_tokens()[0]
    assert datacatalog.tokens.validate_token(token, salt, permissive=False) is True

def test_validate_admin_token(salt):
    token = datacatalog.tokens.get_admin_tokens()[0]
    assert datacatalog.tokens.validate_admin_token(token, permissive=False) is True

def test_validate_admin_token_false(salt):
    token = 'gmw6jqb3r5ts1b2y'
    with pytest.raises(ValueError):
        datacatalog.tokens.validate_admin_token(token, permissive=False) is True

def test_validate_admin_token_env(salt, monkeypatch):
    monkeypatch.setenv('CATALOG_RESET_TOKEN', 'gmw6jqb3r5ts1b2y')
    token = datacatalog.tokens.get_admin_tokens()[0]
    assert datacatalog.tokens.validate_admin_token(token, permissive=False) is True
    # A random invalid token
    token = 'wxapoi0hoqgye02r'
    with pytest.raises(ValueError):
        datacatalog.tokens.validate_admin_token(token, permissive=False) is True
