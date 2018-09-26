
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

DNS_FOR_NAMESPACE = 'sd2e.org'
UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_FOR_NAMESPACE)

class AgaveSystems(object):
    storage = {'data-sd2e-community': {
        'system_id': 'data-sd2e-community',
        'aliases': ['sd2e-community', 'sd2e_community'],
        'root_dir': '/work/projects/SD2E-Community/prod/data',
        'pagesize': 50}}

class Constants(object):
    DNS_FOR_NAMESPACE = 'sd2e.org'
    MOCK_DNS_FOR_NAMESPACE = 'sd2e.club'
    UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_FOR_NAMESPACE)
    UUID_MOCK_NAMESPACE = uuid3(NAMESPACE_DNS, MOCK_DNS_FOR_NAMESPACE)
    ABACO_HASHIDS_SALT = 'eJa5wZlEX4eWU'
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
