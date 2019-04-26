import os
from .helpers import fix_assets_path, array_from_string, parse_boolean, int_or_none, set_from_string

__all__ = ['DEBUG_MODE', 'RECORD_PROPERTIES_SOURCE']

DEBUG_MODE = parse_boolean(
    os.environ.get('LOCALONLY', os.environ.get('DEBUG', 'false')))

# A text flag in each record indicating its source. Used primarily to
# make it very clear whether records are from testing behavior
# TODO - Add this to basestore template for _properties.source
RECORD_PROPERTIES_SOURCE = os.environ.get(
    'CATALOG_RECORDS_SOURCE', 'testing')
