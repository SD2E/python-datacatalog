import hashlib
import base64
from os import environ

TOKEN_LENGTH = 16
"""Generated token length"""

from ..debug_mode import debug_mode

TOKEN_ENVS_DEFAULTS = [
    ('CATALOG_RESET_TOKEN', 'f9mr79w44x96ojj8'),
    ('CATALOG_DELETE_TOKEN', 'b2hhb7s470owrvtd')
]

class InvalidToken(ValueError):
    """Raised when a token is invalid"""
    pass

class Token(str):
    """An update token"""
    def __new__(cls, value, scope='user'):
        value = str(value).lower()
        setattr(cls, 'scope', scope)
        return str.__new__(cls, value)

def get_admin_tokens():
    toks = list()
    for e, d in TOKEN_ENVS_DEFAULTS:
        toks.append(environ.get(e, d))
    return toks

def get_token(salt, *args):
    """Deterministically generates a token from an argument set

    Tokens provide a minimal signature that can be used to authorize edits
    to a record managed by datacatalog.

    Args:
        salt (str):

    Returns:
        Token: An alphanumeric token
    """
    argset = [salt]
    argset.extend(args)
    str_argset = [str(a) for a in argset if True]
    msg = ':'.join(str_argset)
    return Token(hashlib.sha256(msg.encode('utf-8')).hexdigest()[0:TOKEN_LENGTH])

def validate_admin_token(token, permissive=True):
    # Local testing scope
    toks = get_admin_tokens()
    if debug_mode() is True:
        return True
    # Admin tokens
    if token in toks:
        return True
    if permissive:
        return False
    else:
        raise InvalidToken('Administrative token was not valid')

def validate_token(token, salt, *args, permissive=True):
    # Local testing scope
    if debug_mode() is True:
        return True
    # Allow override
    if validate_admin_token(token, permissive=True):
        return True
    else:
        test_token = get_token(salt, *args)
        if token == test_token:
            return True
        else:
            if permissive:
                return False
            else:
                raise InvalidToken('Token was not valid')
