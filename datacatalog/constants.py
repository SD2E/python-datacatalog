
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object

import os
from attrdict import AttrDict
from uuid import uuid3, NAMESPACE_DNS

__version__ = 3
DNS_DOMAIN = 'sd2e.org'
UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_DOMAIN)

class AgaveSystems(object):
    storage = {'data-sd2e-community': {
        'system_id': 'data-sd2e-community',
        'aliases': ['sd2e-community', 'sd2e_community'],
        'root_dir': '/work/projects/SD2E-Community/prod/data',
        'pagesize': 50}}

class Constants(object):
    DNS_DOMAIN = 'sd2e.org'
    MOCK_DNS_DOMAIN = 'sd2e.club'
    UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_DOMAIN)
    UUID_MOCK_NAMESPACE = uuid3(NAMESPACE_DNS, MOCK_DNS_DOMAIN)
    ABACO_HASHIDS_SALT = 'eJa5wZlEX4eWU'
    TYPEDUUID_HASHIDS_SALT = 'xCPJ7PKTdp8BYYb4twh9xNYD'
    MOCK_IDS_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'
    JOBS_TOKEN_SALT = '3MQXA&jk/-![^7+3'
    PIPELINES_TOKEN_SALT = 'h?b"xM6!QH`86qU3'
    UPLOADS_ROOT = 'uploads'
    PRODUCTS_ROOT = 'products'
    REFERENCES_ROOT = 'reference'
    CATALOG_AGAVE_STORAGE_SYSTEM = os.environ.get(
        'CATALOG_STORAGE_SYSTEM', 'data-sd2e-community')
    CATALOG_AGAVE_ROOT_DIR = os.environ.get(
        'CATALOG_ROOT_DIR', AgaveSystems.storage[CATALOG_AGAVE_STORAGE_SYSTEM]['root_dir'])
    CATALOG_MONGODB_HOST = os.environ.get('CATALOG_MONGODB_HOST', 'catalog.sd2e.org')
    CATALOG_MONGODB_PORT = os.environ.get('CATALOG_MONGODB_PORT', 27020)

class Enumerations(object):
    LABPATHS = ('ginkgo', 'transcriptic', 'biofab', 'emerald')
    LABNAMES = ('Ginkgo', 'Transcriptic', 'UW_BIOFAB', 'Emerald')
    CHALLENGE_PROBLEMS = ('Yeast-Gates', 'Novel-Chassis')

class Mappings(object):
    LABPATHS = {'ginkgo': 'Ginkgo', 'transcriptic': 'Transcriptic', 'biofab': 'UW_BIOFAB', 'emerald': 'Emerald'}

class CatalogStore(object):
    debug = False
    uuid5_namespace = Constants.UUID_NAMESPACE
    agave_storage_system = Constants.CATALOG_AGAVE_STORAGE_SYSTEM
    agave_root_dir = Constants.CATALOG_AGAVE_ROOT_DIR
    uploads_dir = Constants.UPLOADS_ROOT
    products_dir = Constants.PRODUCTS_ROOT
    references_dir = Constants.REFERENCES_ROOT
    collections = {'updates': 'updates',
                   'fixity': 'datafiles',
                   'files': 'files',
                   'challenges': 'challenges',
                   'experiments': 'experiments',
                   'samples': 'samples',
                   'measurements': 'measurements',
                   'pipelines': 'pipelines',
                   'jobs': 'jobs',
                   'tokens': 'tokens',
                   'products_files': 'products_files',
                   'products_files_fixity': 'products_files_fixity',
                   'reference_files': 'reference_files',
                   'reference_files_fixity': 'reference_files_fixity'}
    batch = 1000
    mongodb = {'host': 'catalog.sd2e.org',
               'port': '27020', 'username': None,
               'password': None, 'replica_set': None}
