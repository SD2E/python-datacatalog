import os
from .helpers import fix_assets_path, array_from_string, parse_boolean, int_or_none, set_from_string

__all__ = ['MONGODB_HOST', 'MONGODB_PORT',
           'MONGODB_USERNAME', 'MONGODB_PASSWORD',
           'MONGODB_DATABASE', 'MONGODB_AUTH_DATABASE',
           'MONGODB_REPLICA_SET', 'MONGODB_AUTHN',
           'MONGO_DELETE_FIELD']

MONGODB_HOST = os.environ.get('CATALOG_MONGODB_HOST', 'catalog.sd2e.org')
MONGODB_PORT = int(os.environ.get('CATALOG_MONGODB_PORT', '27020'))
MONGODB_USERNAME = os.environ.get('CATALOG_MONGODB_USERNAME', 'readwrite')
MONGODB_PASSWORD = os.environ.get('CATALOG_MONGODB_PASSWORD', '$user!<123')
MONGODB_DATABASE = os.environ.get('CATALOG_MONGODB_DATABASE', 'catalog')
MONGODB_AUTH_DATABASE = os.environ.get('CATALOG_MONGODB_AUTH_DATABASE', 'admin')
MONGODB_REPLICA_SET = os.environ.get('CATALOG_MONGODB_REPLICA_SET', 'rs0')
MONGODB_AUTHN = os.environ.get('CATALOG_MONGODB_AUTHN', '')
MONGODB_PAGESIZE = int(os.environ.get('CATALOG_MONGODB_PAGESIZE', '-1'))
# MongoDB field used to mark records as active or deleted
MONGO_DELETE_FIELD = '_visible'
