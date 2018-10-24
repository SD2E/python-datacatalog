
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

from .constants import Constants
from .datacatalog_uuidtype import UUIDTYPES

class TypedUUID(object):
    def __init__(self, *args):
        self.key = args[0]
        self.prefix = args[1]
        self.title = args[2]

    def __len__(self):
        return len(self.prefix)

UUIDType = dict()
for uuidt, prefix, title in UUIDTYPES:
    UUIDType[uuidt] = TypedUUID(uuidt, prefix, title)

def validate_type(type_string):
    """Ensure that the provided type string is valid"""
    if type_string.lower() in list(UUIDType.keys()):
        return True
    else:
        raise ValueError('{} is not a known Catalog UUIDType'.format(type_string))

def generate(text_value=None, uuid_type=None, binary=True):
    # if isinstance(text_value, (list, tuple)):
    #     text_value = ':'.join(sorted(text_value))
    if text_value is None:
        text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, uuid_type, binary)

def random_uuid5(binary=True):
    text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, binary, namespace=Constants.UUID_NAMESPACE)

def mock(text_value=None, uuid_type=None, binary=True):
    if text_value is None:
        text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, uuid_type, binary, namespace=Constants.UUID_MOCK_NAMESPACE)

def validate(uuid_string, permissive=False):
    return validate_uuid5(uuid_string, permissive=permissive)

def get_uuidtype(query_uuid):
    """Determine the datacatalog.identifiers.UUIDType for a UUID

    Params:
    query_uuid: accepts either a string representation of UUID or a UUUD object

    Returns:
    UUIDType:string
    """
    if isinstance(query_uuid, uuid.UUID):
        query_uuid = str(query_uuid)
    uuid_end = query_uuid[:3].lower()
    for t, v in UUIDType.items():
        if uuid_end == v.prefix:
            return t
    raise ValueError('{} is not a known UUIDType'.format(query_uuid))

def catalog_uuid(text_value, uuid_type='generic', namespace=Constants.UUID_NAMESPACE, binary=False):
    """Returns a typed UUID5 in the prescribed namespace

    Args:
        text_value:string - a text string to encode as UUID hash
        type:string - a known datacatalog UUIDType
        binary (bool): whether to encode result as BSON binary
    Returns:
        new_uuid: The hash UUID in string or binary-encoded form
    """

    uuidtype_tag = UUIDType[uuid_type].prefix
    new_uuid = uuid.uuid5(namespace, text_value)
    new_typed_uuid = uuid.UUID(uuidtype_tag + new_uuid.hex[len(uuidtype_tag):])

    if binary is False:
        return str(new_typed_uuid)
    else:
        return Binary(new_typed_uuid.bytes, OLD_UUID_SUBTYPE)

def text_uuid_to_binary(text_uuid):
    try:
        return Binary(uuid.UUID(text_uuid).bytes, OLD_UUID_SUBTYPE)
    except Exception as exc:
        raise ValueError('Failed to convert text UUID to binary', exc)

def binary_uuid_to_text(binary_uuid):
    try:
        print(type(binary_uuid))
        return str(uuid.UUID(bytes=binary_uuid))
    except Exception as exc:
        raise ValueError('Failed to convert binary UUID to string', exc)

def validate_uuid5(uuid_string, permissive=False):
    """
    Validate that a UUID string is in fact a valid uuid5.
    """
    try:
        uuid.UUID(uuid_string, version=5)
        return True
    except ValueError:
        if permissive is False:
            raise ValueError('{} is not a valid UUID5'.format(uuid_string))
        else:
            return False
