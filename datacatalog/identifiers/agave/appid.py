import re
from ..schemas import IdentifierSchema, JSONSchemaCollection
from .examples import AGAVE_APP_ID as EXAMPLES

PROPERTIES = {'id': 'agave_appid',
              'title': 'Agave appID',
              'description': 'Agave appID identifier',
              'type': 'string'}

__all__ = ["generate", "validate", "mock", "get_schemas"]

# These values are derived from:
# agave-flat/agave-apps/apps-core/src/main/java/org/iplantc/service/apps/model/Software.java
APPID_REGEX = '(^[a-zA-Z0-9_\\-\\.]+)\\-((?:0|[1-9]+[\\d]*)[\\.\\d]+)(u[0-9]+)?$'
"""Regular expression for detecting an Agave appId"""
APPID_MAX_LENGTH = 64
"""Maximum length for an Agave appId"""

__all__ = ["validate", "get_schemas"]

def mock():
    """Create a mock Agave appId

    This is useful for testing.

    Returns:
        str: The new appId
    """
    raise NotImplementedError()

def generate():
    """Create a new Agave appId

    This is useful for testing.

    Returns:
        str: The new appId
    """
    return mock()

def validate(text_string, permissive=False):
    """Validate whether a string is an Agave appId

    Args:
        text_string (str): the value to validate
        permissive (bool, optional): whether to return false or raise Exception on failure

    Raises:
        ValueError: The passed value was not an appId and permissive was `False`

    Returns:
        bool: Whether the passed value is an Agave appId
    """
    result = is_appid(text_string)
    if result is True:
        return result
    else:
        if permissive is False:
            raise ValueError(
                '{} is not a valid Agave appId'.format(text_string))
        else:
            return False

def is_appid(textString, useApi=False, agaveClient=None):
    if len(textString) > APPID_MAX_LENGTH:
        return False
    if re.match(APPID_REGEX, textString):
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
