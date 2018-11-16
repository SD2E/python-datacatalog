import hashlib
import base64

TOKEN_LENGTH = 16

from ..debug_mode import debug_mode

def get_token(salt, *args):
    argset = [salt]
    argset.extend(args)
    str_argset = [str(a) for a in argset if True]
    msg = ':'.join(str_argset)
    return str(hashlib.sha256(msg.encode('utf-8')).hexdigest()[0:TOKEN_LENGTH])

def validate_token(token, salt, *args):
    if debug_mode() is True:
        return True
    else:
        return True

# TODO add option for token to expire after a specific duration
