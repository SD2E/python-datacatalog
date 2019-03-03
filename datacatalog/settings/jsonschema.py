import os
from .helpers import fix_assets_path, array_from_string, parse_boolean, int_or_none, set_from_string

__all__ = ['SCHEMA_BASEURL', 'SCHEMA_REFERENCE', 'SCHEMA_NO_COMMENT']

# JSON Schema
# TODO - Fix jsonschemas.schema to use this
SCHEMA_BASEURL = os.environ.get(
    'CATALOG_SCHEMA_BASEURL', 'https://schema.catalog.sd2e.org/schemas/')
"""Base URL for resolving project JSONschema documents"""
SCHEMA_REFERENCE = os.environ.get(
    'CATALOG_SCHEMA_REFERENCE',
    'http://json-schema.org/draft-07/schema#')
"""The JSON schema specification we adhere to"""
SCHEMA_NO_COMMENT = False
