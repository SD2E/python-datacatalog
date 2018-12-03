
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *

import uuid
from hashids import Hashids

from .. import constants

__all__ = ["generate", "validate", "mock"]

def generate():
    return get_id()

def validate(text_string, permissive=False):
    """Validate whether a string is a hashid

    Args:
        text_string (str): the value to validate
        permissive (bool, optional): whether to return false or raise Exception on failure

    Raises:
        ValueError: The passed value was not a Hashid and permissive was `False`

    Returns:
        bool: Whether the passed value is a Hashid

    Warning:
        This is better for opt-in classification than formal valdiation as there are several edge cases than can render a false negative.
    """
    result = is_hashid(text_string)
    if result is True:
        return result
    else:
        if permissive is False:
            raise ValueError(
                '{} is not a valid abaco hashid'.format(text_string))
        else:
            return False

def mock():
    """Create a Hashid that will not validate

    This is useful for testing.

    Returns:
        str: The new Hashid
    """
    return get_id(salt=constants.Constants.MOCK_IDS_SALT)

def get_id(salt=constants.Constants.ABACO_HASHIDS_SALT):
    """Create a new Hashid

    This is useful for testing.

    Args:
        salt (str, optional): Salt value for generating the hash.

    Returns:
        str: The new Hashid
    """
    hashids = Hashids(salt=salt)
    _uuid = uuid.uuid1().int >> 64
    return hashids.encode(_uuid)

def is_hashid(identifier):
    hashids = Hashids(salt=constants.Constants.ABACO_HASHIDS_SALT)
    dec = hashids.decode(identifier)
    if len(dec) > 0:
        return True
    else:
        return False
