import os
from .helpers import fix_assets_path, array_from_string, parse_boolean, int_or_none, set_from_string

__all__ = ['ABACO_HASHIDS_SALT', 'TYPEDUUID_HASHIDS_SALT', 'MOCK_IDS_SALT',
           'JOBS_TOKEN_SALT', 'PIPELINES_TOKEN_SALT', 'ADMIN_TOKEN_KEY',
           'ADMIN_TOKEN_SECRET', 'ADMIN_TOKEN_LIFETIME', 'TOKEN_LENGTH',
           'SALT_LENGTH']

TOKEN_LENGTH = int(os.environ.get('CATALOG_TOKEN_LENGTH', '16'))
SALT_LENGTH = int(os.environ.get('CATALOG_SALT_LENGTH', '16'))

ABACO_HASHIDS_SALT = 'eJa5wZlEX4eWU'
TYPEDUUID_HASHIDS_SALT = os.environ.get(
    'CATALOG_TYPEDUUID_HASHIDS_SALT', 'xCPJ7PKTdp8BYYb4twh9xNYD')
MOCK_IDS_SALT = os.environ.get(
    'CATALOG_MOCK_IDS_SALT', '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve')

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
    'CATALOG_ADMIN_TOKEN_LIFETIME', '300'))
"""Lifetime in seconds for administrative tokens"""
