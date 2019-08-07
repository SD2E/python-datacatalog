import os
# from funcy import distinct, remove
from .helpers import fix_assets_path, array_from_string, parse_boolean, int_or_none, set_from_string
from .organization import *
from .callbacks import *
from .crypt import *
from .debug import *
from .identifiers import *
from .jsonschema import *
from .mongo import *

def all_settings():
    from types import ModuleType

    settings = {}
    for name, item in globals().iteritems():
        if not callable(item) and not name.startswith("__") and not isinstance(item, ModuleType):
            settings[name] = item
    return settings

# TODO - Add code and a build target that walks settings to generate an example Dockerfile w envs

# TypedUUID
# UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_DOMAIN)

# Managed storage defaults
STORAGE_SYSTEM = os.environ.get(
    'CATALOG_STORAGE_SYSTEM', TACC_PRIMARY_STORAGE_SYSTEM)
STORAGE_MANAGED_VERSION = os.environ.get(
    'CATALOG_STORAGE_MANAGED_VERSION', 'v2')

TAPIS_ANY_AUTHENTICATED_USERNAME = 'world'
TAPIS_UNAUTHENTICATED_USERNAME = 'public'

# Managed stores
UPLOADS_ROOT = os.environ.get('CATALOG_UPLOADS_ROOT', 'uploads')
UPLOADS_SYSTEM = os.environ.get('CATALOG_UPLOADS_SYSTEM', STORAGE_SYSTEM)
UPLOADS_VERSION = os.environ.get('CATALOG_UPLOADS_VERSION', STORAGE_MANAGED_VERSION)
PRODUCTS_ROOT = os.environ.get('CATALOG_PRODUCTS_ROOT', 'products')
PRODUCTS_SYSTEM = os.environ.get('CATALOG_PRODUCTS_SYSTEM', STORAGE_SYSTEM)
PRODUCTS_VERSION = os.environ.get('CATALOG_PRODUCTS_VERSION', STORAGE_MANAGED_VERSION)
REFERENCES_ROOT = os.environ.get('CATALOG_REFERENCES_ROOT', 'references')
REFERENCES_SYSTEM = os.environ.get('CATALOG_PREFERENCES_SYSTEM', STORAGE_SYSTEM)
REFERENCES_VERSION = os.environ.get('CATALOG_REFERENCES_VERSION', STORAGE_MANAGED_VERSION)

# Path naming preferences
UNICODE_PATHS = parse_boolean(os.environ.get('CATALOG_UNICODE_PATHS', '0'))

# Contents of record._admin.source
RECORDS_SOURCE = os.environ.get('CATALOG_RECORDS_SOURCE', 'testing')

# Prefix for minting file.id strings
FILE_ID_PREFIX = os.environ.get('CATALOG_FILE_ID_PREFIX', 'file.tacc') + '.'

LOG_LEVEL = os.environ.get('CATALOG_LOG_LEVEL', 'NOTSET')
LOG_FIXITY_ERRORS = parse_boolean(os.environ.get('CATALOG_LOG_FIXITY_ERRORS', '0'))
LOG_UPDATES = parse_boolean(os.environ.get('CATALOG_LOG_UPDATES', '1'))
LOG_VERBOSE = parse_boolean(os.environ.get(
    'CATALOG_LOG_VERBOSE', '0'))
# Maximum number of
MAX_INDEX_FILTERS = int(os.environ.get('CATALOG_MAX_INDEX_FILTERS', '100'))
MAX_INDEX_PATTERNS = int(os.environ.get('CATALOG_MAX_INDEX_PATTERNS', '512'))

# Python JSONschema Objects Cache
PJS_CACHE_MAX_AGE = int(os.environ.get('CATALOG_PJS_CACHE_MAX_AGE', '3600'))
PJS_CACHE_DIR = os.environ.get('CATALOG_PJS_CACHE_DIR', None)
