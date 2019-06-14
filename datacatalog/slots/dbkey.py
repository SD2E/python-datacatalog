import uuid
from hashids import Hashids
from . import constants

DELIMITER = '-'

__all__ = ['new_keyname']


def new_keyname(username):
    """Generates a new, randomized keyname
    """
    elements = [constants.PREFIX, username]
    elements.append(new_hashid())
    return DELIMITER.join(elements)


def new_hashid():
    """Generate a hash id
    """
    hashids = Hashids(salt=constants.HASHID_SALT)
    entropy = uuid.uuid1().int >> 64
    return hashids.encode(entropy)
