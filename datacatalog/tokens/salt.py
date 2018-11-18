import os
import base64

SALT_LENGTH = 16
"""Number of bytes in the salt"""
class Salt(str):
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

def generate_salt(length=SALT_LENGTH):
    """Generates a cryptographic salt

    Args:
        length (int, optional): Length of salt in bytes

    Returns:
        Salt: a salt value
    """
    salt = os.urandom(length)
    return Salt(base64.b64encode(salt).decode('utf-8'))
