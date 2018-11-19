
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import base64
import bson
import uuid

from bson.codec_options import CodecOptions
from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE, STANDARD

from .. import constants
from .datacatalog_uuidtype import UUIDTYPES

class TypedUUID(object):
    """UUID identifying a catalog object and advertising its internal type"""

    def __init__(self, *args):
        self.key = args[0]
        self.prefix = args[1]
        self.title = args[2]

    def __len__(self):
        return len(self.prefix)

UUIDType = dict()
for uuidt, prefix, title in UUIDTYPES:
    UUIDType[uuidt] = TypedUUID(uuidt, prefix, title)

def validate_type(type_string, permissive=False):
    """Ensure a provided type string is valid

    Args:
        type_string (str): String representing a known catalog type
        permissive (vool, optional): Return `False` or raise Exception on failure

    Returns:
        bool: Whether the value is a known type
    """
    if type_string.lower() in list(UUIDType.keys()):
        return True
    else:
        if permissive is False:
            raise ValueError('{} is not a known Catalog UUIDType'.format(type_string))
        else:
            return False

def generate(text_value=None, uuid_type=None, binary=True):
    """Generate a TypedUUID of a specific type from a string

    Args:
        text_value (str): A string to convert into an UUID
        uuid_type (str, optional): The type of UUID to return

    Returns:
        str: String representation of the generated UUID
    """
    if text_value is None:
        text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, uuid_type, binary)

def random_uuid5(binary=True):
    """Generate a random TypedUUID

    Returns:
        str: String representation of the random UUID
    """
    text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, binary, namespace=constants.Constants.UUID_NAMESPACE)

def mock(text_value=None, uuid_type=None, binary=True):
    """Generate a mock TypedUUID of a specific type from a string

    Args:
        text_value (str): A string to convert into an UUID
        uuid_type (str, optional): The type of UUID to return

    Returns:
        str: String representation of the generated UUID

    Note:
        UUID is in a different namespace and will not validate
    """
    if text_value is None:
        text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, uuid_type, binary, namespace=constants.Constants.UUID_MOCK_NAMESPACE)

def validate(uuid_string, permissive=False):
    """Validate whether a string is a valid TypedUUID

    Args:
        uuid_string (str): the value to validate
        permissive (bool, optional): whether to return false or raise Exception on failure

    Raises:
        ValueError: The passed value was not an appId and permissive was `False`

    Returns:
        bool: Validation result
    """
    return validate_uuid5(uuid_string, permissive=permissive)

def get_uuidtype(query_uuid):
    """Determine the TypedUUID type for a UUID

    Args:
        query_uuid (str/uuid.uuid): a UUID

    Raises:
        ValueError: Raised if the query cannot be resolved to a known UUID type

    Returns:
        str: The TypedUUID type for the query
    """
    if isinstance(query_uuid, uuid.UUID):
        query_uuid = str(query_uuid)
    uuid_end = query_uuid[:3].lower()
    for t, v in UUIDType.items():
        if uuid_end == v.prefix:
            return t
    raise ValueError('{} is not a known UUIDType'.format(query_uuid))

def catalog_uuid(text_value, uuid_type='generic', namespace=constants.Constants.UUID_NAMESPACE, binary=False):
    """Returns a TypedUUID5 for text_value

    Args:
        text_value (str): the text string to encode as a UUID5
        type (str, optional): one the known datacatalog UUID types

    Returns:
        str: The new TypedUUID in string form
    """

    uuidtype_tag = UUIDType[uuid_type].prefix
    new_uuid = uuid.uuid5(namespace, text_value)
    new_typed_uuid = uuid.UUID(uuidtype_tag + new_uuid.hex[len(uuidtype_tag):])

    if binary is False:
        return str(new_typed_uuid)
    else:
        return Binary(new_typed_uuid.bytes, OLD_UUID_SUBTYPE)

def text_uuid_to_binary(text_uuid):
    """Convert text TypedUUID to binary form"""
    try:
        return Binary(uuid.UUID(text_uuid).bytes, OLD_UUID_SUBTYPE)
    except Exception as exc:
        raise ValueError('Failed to convert text UUID to binary', exc)

def binary_uuid_to_text(binary_uuid):
    """Convert binary TypeUUID to its text representation"""
    try:
        print(type(binary_uuid))
        return str(uuid.UUID(bytes=binary_uuid))
    except Exception as exc:
        raise ValueError('Failed to convert binary UUID to string', exc)

def validate_uuid5(uuid_string, permissive=False):
    """Test whether a UUID string is a valid uuid.uuid5"""
    try:
        uuid.UUID(uuid_string, version=5)
        return True
    except ValueError:
        if permissive is False:
            raise ValueError('{} is not a valid UUID5'.format(uuid_string))
        else:
            return False
