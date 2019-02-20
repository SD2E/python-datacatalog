#!/usr/bin/env python3
import argparse
import hashlib
import base64
import os
import uuid

TOKEN_LENGTH = 16
"""Number of bytes in a generated token"""

SALT_LENGTH = 16
"""Number of bytes in a generated salt"""

__SECRET_SALTS = {'job': '3MQXA&jk/-![^7+3',
                  'pipeline': 'h?b"xM6!QH`86qU3'}

class Salt(str):
    """Contains a salt value as a string"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class Token(str):
    """Contains a token value as a string"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class InvalidToken(ValueError):
    """Raised if a token fails validation"""
    pass

class InvalidUUID(ValueError):
    """Raised if a UUID string is not a valid UUID"""
    pass

def get_pipeline_token(**kwargs):
    """Retrieves the update token for a Pipeline

    Args:
        pipeline_uuid (str): UUID for the pipeline
        salt (str): The Pipeline's ``salt`` from MongoDB

    Note:
        Only valid for tokens generated by datacatalog==0.1.4

    Returns:
        Token: the Pipeline's update token
    """
    msg = ':'.join(
        [
            __SECRET_SALTS['pipeline'],
            str(kwargs['pipeline_uuid']),
            str(kwargs['salt'])
        ])
    return __get_token(msg)

def get_job_token(**kwargs):
    """Retrieves the update token for a PipelineJob

    Args:
        pipeline_uuid (str): UUID for the pipeline
        job_uuid (str): UUID for the job
        salt (str): The Pipeline's ``salt`` from MongoDB

    Note:
        Only valid for tokens generated by datacatalog==0.1.4

    Returns:
        Token: the PipelineJob's update token
    """
    msg = ':'.join(
        [
            __SECRET_SALTS['job'],
            str(kwargs['pipeline_uuid']),
            str(kwargs['job_uuid']),
            str(kwargs['salt'])
        ])
    return __get_token(msg)

def __get_token(tokenstring):
    return Token(str(hashlib.sha256(
        tokenstring.encode('utf-8')).hexdigest()[0:TOKEN_LENGTH]))

def generate_salt(length=SALT_LENGTH):
    """Generates a cryptographic salt

    Args:
        length (int, optional): Length of salt in bytes

    Returns:
        Salt: a salt value
    """
    salt = os.urandom(length)
    return Salt(base64.b64encode(salt).decode('utf-8'))

def validate_uuid5(uuid_string, permissive=True):
    """
    Confirms that a text UUID validates as UUID5

    Args:
        uuid_string (str): UUID to validate
        permssive (bool, optional): Return False instead of raising an Exception

    Raises:
        ValueError: Raised on failure to validate if ``permissive`` is ``False``
        TypeError: Raised if function is not passed a string

    Returns:
        bool: Whether the value validates as UUID5
    """
    if not isinstance(uuid_string, str):
        raise TypeError('"uuid_string" is required and must be a string')

    try:
        uuid.UUID(uuid_string, version=5)
        return True
    except ValueError:
        if permissive is False:
            raise InvalidUUID('{} is not a valid UUID5'.format(uuid_string))
        else:
            return False

def validate_salt(salt, permissive=True):
    if len(salt) > 0 and isinstance(salt, str):
        return True
    else:
        raise ValueError('Invalid salt value')

def main():
    parser = argparse.ArgumentParser(prog="python -m scripts.fetch_token", description="Regenerate the update token for a pipeline or pipelinejob. Requires knowledge of appropriate UUIDs and the record's salt value.")
    parser.add_argument("tokentype", help="Token type (pipeline or job)", type=str, choices=["job", "pipeline"])
    parser.add_argument("--pipeline", help="Pipeline UUID", type=str)
    parser.add_argument("--job", help="Job UUID", type=str)
    parser.add_argument("--salt", help="Salt value from database", type=str)
    args = parser.parse_args()

    puuid = None
    juuid = None
    saltv = None
    token = None
    ttype = vars(args).get('tokentype')

    try:
        puuid = vars(args).get('pipeline', None)
        saltv = vars(args).get('salt', None)
        juuid = vars(args).get('job', None)

        validate_uuid5(puuid)
        validate_salt(saltv)
        if ttype == 'job':
            validate_uuid5(juuid)

    except Exception:
        raise

    if ttype == 'pipeline':
        token = get_pipeline_token(pipeline_uuid=puuid, salt=saltv)
    elif ttype == 'job':
        token = get_job_token(pipeline_uuid=puuid, job_uuid=juuid, salt=saltv)

    print(token)

if __name__ == '__main__':
    main()
