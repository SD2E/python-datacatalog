import pytest
from time import sleep
from datacatalog import tokens

def test_get_token(crypto_salt):
    token = tokens.get_token(crypto_salt, 'arg1', 'arg2')
    assert isinstance(token, str)

def test_validate_token(crypto_salt):
    token = tokens.get_token(crypto_salt, 'arg1', 'arg2')
    assert tokens.validate_token(
        token, crypto_salt, 'arg1', 'arg2') is True

def test_validate_token_false_permissive(crypto_salt):
    token = tokens.get_token(crypto_salt, 'arg1', 'arg2')
    assert tokens.validate_token(
        token, crypto_salt, 'arg1', 'arg3') is False

def test_validate_token_false(crypto_salt):
    token = tokens.get_token(crypto_salt, 'arg1', 'arg2')
    with pytest.raises(ValueError):
        tokens.validate_token(
            token, crypto_salt, 'arg1', 'arg3', permissive=False)

def test_validate_token_passthru(crypto_salt, admin_key):
    token = tokens.get_admin_token(admin_key)
    assert tokens.validate_token(token, crypto_salt) is True

def test_validate_admin_token_valid(admin_key):
    token = tokens.get_admin_token(admin_key)
    assert tokens.validate_admin_token(token, admin_key, permissive=False) is True

def test_validate_admin_token_env_key_valid(env_override_admin_key):
    k = env_override_admin_key
    token_key_arg = tokens.get_admin_token(k)
    assert tokens.validate_admin_token(
        token_key_arg, k, permissive=False) is True

def test_validate_admin_token_env_secret_valid(env_override_admin_key):
    k = env_override_admin_key
    token = tokens.get_admin_token(k)
    assert tokens.validate_admin_token(token, k, permissive=False) is True

def test_validate_admin_token_passed_valid(admin_key):
    token = tokens.get_admin_token(admin_key)
    assert tokens.validate_admin_token(token, admin_key, permissive=False) is True

def test_validate_admin_token_notpassed_fail(admin_key):
    # Turns off global debug mode
    token = tokens.get_admin_token(admin_key)
    assert token is not None

def test_validate_admin_token_passed_invalid():
    token = 'gmw6jqb3r5ts1b2y'
    with pytest.raises(ValueError):
        tokens.validate_admin_token(token, permissive=False) is True

def test_override_token_ttl(short_token_ttl):
    ttl = short_token_ttl
    assert tokens.get_admin_lifetime() == ttl
    assert tokens.get_admin_lifetime() != 3600

def test_admin_token_ttl(short_token_ttl, env_override_admin_key):
    k = env_override_admin_key
    ttl = short_token_ttl
    ttl_config = tokens.get_admin_lifetime()
    assert ttl == ttl_config
    token = tokens.get_admin_token(key=k)
    assert tokens.validate_admin_token(token, key=k, permissive=False) is True
    sleep(ttl * 2)
    with pytest.raises(tokens.InvalidAdminToken):
        tokens.validate_admin_token(token, key=k, permissive=False) is True
