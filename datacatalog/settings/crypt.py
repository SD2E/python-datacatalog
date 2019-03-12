import os
from .helpers import fix_assets_path, array_from_string, parse_boolean, int_or_none, set_from_string

__all__ = ['JOBS_TOKEN_SALT', 'PIPELINES_TOKEN_SALT', 'ADMIN_TOKEN_KEY',
           'ADMIN_TOKEN_SECRET', 'ADMIN_TOKEN_LIFETIME', 'TOKEN_LENGTH',
           'SALT_LENGTH']

TOKEN_LENGTH = int(os.environ.get('CATALOG_TOKEN_LENGTH', '16'))
SALT_LENGTH = int(os.environ.get('CATALOG_SALT_LENGTH', '16'))

# Token salts and keys
JOBS_TOKEN_SALT = os.environ.get(
    'CATALOG_JOBS_TOKEN_SALT', '3MQXA&jk/-![^7+3')
PIPELINES_TOKEN_SALT = os.environ.get(
    'CATALOG_PIPELINES_TOKEN_SALT' 'h?b"xM6!QH`86qU3')

ADMIN_TOKEN_KEY = os.environ.get(
    'CATALOG_ADMIN_TOKEN_KEY',
    'DRECgp2gBts5M26LmfjZ5dFUzFcTngpbbc54PpJvXwcEv5Z5kkkM63ZKyRNsdELN')
"""Default key for generating admin tokens"""
ADMIN_TOKEN_SECRET = os.environ.get(
    'CATALOG_ADMIN_TOKEN_SECRET', 'T}gLWL-*E%<wWfh9JgV4)Rw;s5MwcB2=')
"""Default secret for generating admin tokens"""
ADMIN_TOKEN_LIFETIME = int(os.environ.get(
    'CATALOG_ADMIN_TOKEN_LIFETIME', '3600'))
"""Lifetime in seconds for administrative tokens"""
