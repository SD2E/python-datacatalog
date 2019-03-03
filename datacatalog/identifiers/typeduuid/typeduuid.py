
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
from pprint import pprint
from hashids import Hashids
from datacatalog import settings

from bson.codec_options import CodecOptions
from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE, STANDARD
from ..identifier import random_string, Identifier
from .uuidtypes import UUIDTYPES, TypedUUID, CatalogUUID

uuidtypes = dict()
for uuidt, prefix, title in UUIDTYPES:
    uuidtypes[uuidt] = TypedUUID(uuidt, prefix, title)

class TypedCatalogUUID(CatalogUUID):
    def __init__(self, **kwargs):
        super(TypedCatalogUUID, self).__init__(**kwargs)
        self._filename = kwargs.get('_filename', None)
        self.title = kwargs.get('title', None)
        self.description = self.title + ' ' + self.description
        self.pattern = '^(uri:urn:)?' + kwargs.get('prefix', '100') + '[0-9a-f]{5}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        setattr(self, 'examples', [generate(
            'Why did it have to be snakes?', uuid_type=kwargs.get('kind', 'generic'), binary=False)])
        super(TypedCatalogUUID, self).update_id()

def uuid_to_hashid(uuid_string, salt=settings.TYPEDUUID_HASHIDS_SALT):
    """Convert a UUID to a HashId to save space. Good for file path building."""
    hashids = Hashids(salt=salt)
    return hashids.encode(uuid.UUID(uuid_string).int)

def validate_type(type_string, permissive=False):
    """Ensure a provided type string is valid

    Args:
        type_string (str): String representing a known catalog type
        permissive (vool, optional): Return `False` or raise Exception on failure

    Returns:
        bool: Whether the value is a known type
    """
    if type_string.lower() in list(uuidtypes.keys()):
        return True
    else:
        if permissive is False:
            raise ValueError('{} not a known type for TypedUUID'.format(type_string))
        else:
            return False

def generate(text_value=None, uuid_type=None, binary=False):
    """Generate a TypedUUID of a specific type from a string

    Args:
        text_value (str): A string to convert into an UUID
        uuid_type (str, optional): The type of UUID to return

    Returns:
        str: String representation of the generated UUID
    """
    if text_value is None:
        text_value = random_string(size=128)
    return catalog_uuid(text_value, uuid_type)

def random_uuid5(binary=True):
    """Generate a random TypedUUID

    Returns:
        str: String representation of the random UUID
    """
    text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, binary)

def mock(text_value=None, uuid_type=None, binary=True):
    """Generate a mock TypedUUID of a specific type from a string

    Args:
        text_value (str): A string to convert into an UUID
        uuid_type (str, optional): The type of UUID to return

    Returns:
        str: String representation of the generated TypedUUID

    Note:
        UUID is in a different namespace and will not validate
    """
    if text_value is None:
        text_value = str(uuid.uuid1().int >> 64) + str(uuid.uuid1().int >> 64)
    return catalog_uuid(text_value, uuid_type, binary,
                        namespace=settings.UUID_MOCK_NAMESPACE)

def validate(uuid_string, permissive=False):
    """Validate whether a string is a TypedUUID

    Args:
        uuid_string (str): the value to validate
        permissive (bool, optional): whether to return false or raise Exception on failure

    Raises:
        ValueError: The passed value was not an appId and permissive was `False`

    Returns:
        bool: Validation result
    """
    if validate_uuid5(uuid_string, permissive=permissive):
        try:
            get_uuidtype(uuid_string)
            return True
        except ValueError:
            if permissive is True:
                return False
            else:
                raise ValueError('Not a valid TypedUUID')

def get_uuidtype(query_uuid):
    """Determine the class for a UUID

    Args:
        query_uuid (str/uuid.uuid): an TypedUUID

    Raises:
        ValueError: Raised if the query cannot be resolved to a known UUID type

    Returns:
        str: The TypedUUID class for the query
    """
    if isinstance(query_uuid, uuid.UUID):
        query_uuid = str(query_uuid)
    uuid_end = query_uuid[:3].lower()
    for t, v in uuidtypes.items():
        if uuid_end == v.prefix:
            return t
    raise ValueError('{} is not a known class of TypedUUID'.format(query_uuid))

def catalog_uuid(text_value, uuid_type='generic',
                 namespace=settings.UUID_NAMESPACE,
                 binary=False):
    """Returns a TypedUUID5 for text_value

    Args:
        text_value (str): the text string to encode as a UUID5
        type (str, optional): one the known datacatalog UUID types

    Returns:
        str: The new TypedUUID in string form
    """

    uuidtype_tag = uuidtypes[uuid_type].prefix
    new_uuid = uuid.uuid5(namespace, text_value)
    new_typeduuid = uuid.UUID(uuidtype_tag + new_uuid.hex[len(uuidtype_tag):])

    if binary is False:
        return str(new_typeduuid)
    else:
        return Binary(new_typeduuid.bytes, OLD_UUID_SUBTYPE)

def catalog_uuid_from_v1_uuid(v1_uuid, uuid_type='generic', binary=False):
    assert isinstance(v1_uuid, str), "v1_uuid must be a string"
    validate_type(uuid_type)
    orig_uuid = uuid.UUID(v1_uuid)
    uuidtype_tag = uuidtypes[uuid_type].prefix
    new_typeduuid = uuid.UUID(uuidtype_tag + orig_uuid.hex[len(uuidtype_tag):])
    if binary is False:
        return str(new_typeduuid)
    else:
        return Binary(new_typeduuid.bytes, OLD_UUID_SUBTYPE)


def text_uuid_to_binary(text_uuid):
    """Convert text TypedUUID to binary form"""
    try:
        return Binary(uuid.UUID(text_uuid).bytes, OLD_UUID_SUBTYPE)
    except Exception as exc:
        raise ValueError('Failed to convert text UUID to binary', exc)

def binary_uuid_to_text(binary_uuid):
    """Convert binary TypeUUID to its text representation"""
    try:
        # print(type(binary_uuid))
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
