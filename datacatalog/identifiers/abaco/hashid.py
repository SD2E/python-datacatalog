import uuid
from hashids import Hashids
from datacatalog import settings
from ..schemas import IdentifierSchema, JSONSchemaCollection

PROPERTIES = {'id': 'hashid',
              'title': 'Hashid',
              'description': 'A Hashid identifier',
              'type': 'string'}

__all__ = ["generate", "validate", "mock",
           "IdentifierSchema", "JSONSchemaCollection"]

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
    return get_id(salt=settings.MOCKUUIDS_SALT)

def get_id(salt=settings.ABACO_HASHIDS_SALT):
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
    hashids = Hashids(salt=settings.ABACO_HASHIDS_SALT)
    dec = hashids.decode(identifier)
    if len(dec) > 0:
        return True
    else:
        return False

def get_schemas():
    schemas = dict()
    doc = {'_filename': PROPERTIES['id'],
           'description': PROPERTIES['description'],
           'type': PROPERTIES['type']}
    sch = IdentifierSchema(**doc).to_jsonschema()
    schemas[PROPERTIES['id']] = sch
    return JSONSchemaCollection(schemas)
