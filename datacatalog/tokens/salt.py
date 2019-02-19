import os
import base64
from .. import settings
from .classes import Salt

def generate_salt(length=settings.SALT_LENGTH):
    """Generates a cryptographic salt

    Args:
        length (int, optional): Length of salt in bytes

    Returns:
        Salt: a salt value
    """
    salt = os.urandom(length)
    return Salt(base64.b64encode(salt).decode('utf-8'))
