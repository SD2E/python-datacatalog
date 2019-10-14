import os
import time
import hashlib
from datacatalog import settings
from .classes import Token
from .exceptions import InvalidAdminToken

__all__ = ['InvalidAdminToken', 'get_admin_token', 'validate_admin_token',
           'internal_get_admin_token', 'get_admin_key', 'get_admin_lifetime']

def get_admin_token(key, previous=False):
    """Returns a token with administrative priviledges

    Administrative tokens provide a signature that can be used to authorize
    edits and to trigger specific administrative events.

    Args:
        key (str): The key for generating admin tokens
        previous (bool, optional): Retrieve the most recently issued token for this key

    Returns:
        Token
    """
    if key is None:
        raise ValueError('Value for "key" was expected')
    expires = get_admin_lifetime()
    secret = __get_admin_salt()
    argset = [secret, key]
    ts = int(time.time())
    if previous:
        ts = ts - expires
    argset.extend(str(int(ts / expires)))
    str_argset = [str(a) for a in argset if True]
    msg = ':'.join(str_argset)
    tok = Token(hashlib.sha256(msg.encode('utf-8')).hexdigest()[
        0:settings.TOKEN_LENGTH])
    return tok

def validate_admin_token(token, key=None, permissive=True):
    """Validate an adminstrative token

    Only administrative tokens can be validated using this function.

    Args:
        token (str): The token to validate
        key (str): The "token_key" value used to generate the token
        permissive (bool, optional): Whether to error or return a Boolean on failure

    Raises:
        InvalidAdminToken: The outcome when validation fails and permissive is not set.

    Returns:
        bool: If permissive is set, validity is a Boolean value
    """

    toks = __get_admin_tokens(key)
    if token in toks:
        return True
    if permissive:
        return False
    else:
        raise InvalidAdminToken('Administrative token was not valid')

def internal_get_admin_token(key=None):
    return __get_admin_tokens(key=key)[0]

def __get_admin_tokens(key=None):
    """Gets current and previous token for a key.
    """
    toks = list()
    if key is None:
        key = get_admin_key()
    toks.append(get_admin_token(key))
    toks.append(get_admin_token(key, previous=True))
    return toks

def __get_admin_salt():
    """Internal: Get current secret for generating admin tokens
    """
    return os.environ.get(
        'CATALOG_ADMIN_TOKEN_SECRET', settings.ADMIN_TOKEN_SECRET)

def get_admin_key():
    """Get current  key for generating admin tokens
    """
    return os.environ.get(
        'CATALOG_ADMIN_TOKEN_KEY', settings.ADMIN_TOKEN_KEY)

def get_admin_lifetime():
    """Get current  expiration time (seconds) for new admin tokens
    """
    return int(
        os.environ.get(
            'CATALOG_ADMIN_TOKEN_LIFETIME', settings.ADMIN_TOKEN_LIFETIME))
