import hashlib
import base64

TOKEN_LENGTH = 16
"""Generated token length"""

from ..debug_mode import debug_mode

class InvalidToken(ValueError):
    """Raised when a token is invalid"""
    pass

class Token(str):
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

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

def validate_token(token, salt, *args, permissive=True):
    if debug_mode() is True:
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
