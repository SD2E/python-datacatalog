import re
from ..schemas import IdentifierSchema, JSONSchemaCollection

ROLE_USERNAMES = ('public', 'world')
EXAMPLES = ['taco', 'bb789', 'pwc5ycsd']
PROPERTIES = {'id': 'tacc_username',
              'title': 'TACC.cloud username',
              'description': '',
              'type': 'string'}

__all__ = ["generate", "validate", "mock", "get_schemas"]

UNAME_REGEX = '^[a-z][[a-zA-Z0-9]{2,7}$'
"""Regular expression for a TACC (old-school UNIX) username"""
UNAME_LENGTHS = (3, 9)
"""Length range for a TACC username"""

__all__ = ["validate", "get_schemas"]

def mock():
    """Create a mock TACC.cloud username

    This is useful for testing.

    Returns:
        str: The new username
    """
    raise NotImplementedError()

def generate():
    """Create a new TACC.cloud username

    This is useful for testing.

    Returns:
        str: The new username
    """
    return mock()

def validate(text_string, permissive=False):
    """Validate whether a string can be a TACC.cloud username

    Args:
        text_string (str): the value to validate
        permissive (bool, optional): whether to return false or raise Exception on failure

    Raises:
        ValueError: Passed value fails validation and `permissive` was `False`

    Returns:
        bool: Whether the passed value can be a TACC username
    """
    result = is_username(text_string)
    if result is True:
        return result
    else:
        if permissive is False:
            raise ValueError(
                '{} does not meet formatting rules for a TACC username'.format(text_string))
        else:
            return False

def is_username(textString, useApi=False, agaveClient=None):
    if not isinstance(textString, str):
        return False
    if len(textString) > UNAME_LENGTHS[1]:
        return False
    if len(textString) < UNAME_LENGTHS[0]:
        return False
    if re.match(UNAME_REGEX, textString):
        return True
    else:
        return False

def get_schemas():
    schemas = dict()
    doc = {'_filename': PROPERTIES['id'],
           'description': PROPERTIES['description'],
           'type': PROPERTIES['type'],
           'examples': EXAMPLES}
    sch = IdentifierSchema(**doc).to_jsonschema()
    schemas[PROPERTIES['id']] = sch
    return JSONSchemaCollection(schemas)
