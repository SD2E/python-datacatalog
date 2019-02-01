import time
import hashlib
from os import environ
from ..debug_mode import debug_mode
from .config import TOKEN_LENGTH
from .classes import Token
from .exceptions import InvalidAdminToken

ADMIN_TOKEN_KEY = 'XB]6f^~T3)EDxB(3A6F@CE>JTU.T>whH'
"""Default key for generating admin tokens"""
ADMIN_TOKEN_SECRET = 'T}gLWL-*E%<wWfh9JgV4)Rw;s5MwcB2='
"""Default secret for generating admin tokens"""
ADMIN_TOKEN_LIFETIME = 30
"""Lifetime in seconds for administrative tokens"""

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
    tok = Token(hashlib.sha256(msg.encode('utf-8')).hexdigest()[0:TOKEN_LENGTH])
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

def get_admin_lifetime():
    """Returns the expiration time for newly-minted tokens
    """
    return int(environ.get(
        'CATALOG_ADMIN_TOKEN_LIFETIME', ADMIN_TOKEN_LIFETIME))

def __get_admin_tokens(key=None):
    """Gets current and previous token for a key.
    """
    toks = list()
    toks.append(get_admin_token(key))
    toks.append(get_admin_token(key, previous=True))
    return toks

def __get_admin_salt():
    return environ.get('CATALOG_ADMIN_SALT', ADMIN_TOKEN_SECRET)

def get_admin_key():
    return environ.get('CATALOG_ADMIN_TOKEN_KEY', ADMIN_TOKEN_KEY)

