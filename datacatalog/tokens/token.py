import hashlib
import base64
import time
from os import environ
from .config import TOKEN_LENGTH
from ..debug_mode import debug_mode
from .classes import Token
from .exceptions import InvalidToken
from .admin import validate_admin_token, __get_admin_salt, get_admin_key

def get_token(salt, *args):
    """Deterministically generates a token from arguments

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

def validate_token(token, salt=None, *args, permissive=True):
    """Validate a token

    Both record-level tokens and administrative tokens can be validated using
    this function.

    Args:
        token (str): The token to validate
        salt (str): The "salt" value used to generate the token
        permissive (bool, optional): Whether to error or return a Boolean on failure

    Raises:
        InvalidToken: The outcome when validation fails and permissive is not set.

    Returns:
        bool: If permissive is set, validity is a Boolean value
    """

    # Allow override
    # Since this is an internal call to check if the token is an admin, we pull
    # the token_admin_key to use in validation
    if validate_admin_token(token,
                            key=get_admin_key(), permissive=True):
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
