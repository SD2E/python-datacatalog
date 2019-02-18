from ...tenancy.config import current_tenant
from .hashid import IdentifierSchema, JSONSchemaCollection
from .examples import ABACO_NONCE_ID as EXAMPLES

from . import hashid

PROPERTIES = {'id': 'abaco_nonceid',
              'title': 'Abaco nonceId',
              'description': 'Identifier for an Abaco nonce',
              'type': 'string'}

__all__ = ["generate", "validate", "mock", "get_schemas"]

def current_tenant_prefix():
    tenant_name = current_tenant()
    tenant_prefix = tenant_name.split(sep='.')[0].upper()
    return tenant_prefix

def generate():
    return current_tenant_prefix() + '_' + hashid.generate()

def mock():
    return current_tenant_prefix() + '_' + hashid.mock()

def validate(text_string, permissive=False):
    """Validate whether a string is an Abaco nonce

    Args:
        text_string (str): the value to validate
        permissive (bool, optional): whether to return false or raise Exception on failure

    Raises:
        ValueError: The passed value was not a Nonce and permissive was `False`

    Returns:
        bool: Whether the passed value is a Nonce

    Warning:
        This is better for opt-in classification than formal valdiation as there are several edge cases than can render a false negative.
    """
    pfx = current_tenant_prefix()
    parts = text_string.split('_')
    try:
        if parts[0] != pfx:
            raise ValueError(
                'Prefix {} is incorrect'.format(pfx))
        if not hashid.validate(parts[1], permissive=True):
            raise ValueError('Not a valid Abaco nonce')
        return True
    except ValueError:
        if permissive:
            return False
        else:
            raise

def get_schemas():
    schemas = dict()
    doc = {'_filename': PROPERTIES['id'],
           'description': PROPERTIES['description'],
           'type': PROPERTIES['type']}
    sch = IdentifierSchema(**doc).to_jsonschema()
    schemas[PROPERTIES['id']] = sch
    return JSONSchemaCollection(schemas)
