import os
from uuid import uuid3, NAMESPACE_DNS
from .helpers import fix_assets_path, array_from_string, parse_boolean, int_or_none, set_from_string

__all__ = ['ABACO_HASHIDS_SALT', 'TYPEDUUID_HASHIDS_SALT',
           'MOCKUUIDS_SALT', 'UUID_NAMESPACE', 'UUID_MOCK_NAMESPACE',
           'ADJ_ANIMAL_WORDS', 'ADJ_ANIMAL_LENGTH',
           'ADJ_ANIMAL_DELIM', 'ADJ_ANIMAL_DATE_FORMAT']

ABACO_HASHIDS_SALT = 'eJa5wZlEX4eWU'

UUID_DNS_DOMAIN = os.environ.get('CATALOG_DNS_DOMAIN', 'sd2e.org')
UUID_NAMESPACE = uuid3(NAMESPACE_DNS, UUID_DNS_DOMAIN)
UUID_MOCK_NAMESPACE = uuid3(NAMESPACE_DNS, 'tacc.cloud.dev')

TYPEDUUID_HASHIDS_SALT = os.environ.get(
    'CATALOG_TYPEDUUID_HASHIDS_SALT', 'xCPJ7PKTdp8BYYb4twh9xNYD')
MOCKUUIDS_SALT = os.environ.get(
    'CATALOG_MOCK_IDS_SALT', '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve')

# Configure the adjective animal identifier type
ADJ_ANIMAL_WORDS = int_or_none(os.environ.get(
    'CATALOG_ADJ_ANIMAL_WORDS', '2'))
ADJ_ANIMAL_LENGTH = int_or_none(os.environ.get(
    'CATALOG_ADJ_ANIMAL_LENGTH', '8'))
ADJ_ANIMAL_DELIM = os.environ.get(
    'CATALOG_ADJ_ANIMAL_DELIM', '-')
ADJ_ANIMAL_DATE_FORMAT = os.environ.get(
    'CATALOG_ADJ_DATE_FORMAT', 'YYYYMMDDTHHmmss')
