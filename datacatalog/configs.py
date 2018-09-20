from .constants import *

class CatalogStore():
    debug = False
    uuid5_namespace = Constants.UUID_NAMESPACE
    agave_storage_system = Constants.CATALOG_AGAVE_STORAGE_SYSTEM
    agave_root_dir = Constants.CATALOG_AGAVE_ROOT_DIR
    uploads_dir = Constants.UPLOADS_ROOT
    products_dir = Constants.PRODUCTS_ROOT
    references_dir = Constants.REFERENCES_ROOT
    collections = {'updates': 'updates',
                   'fixity': 'files-fixity',
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
                   'inputs_files': 'inputs_files',
                   'inputs_files_fixity': 'inputs_files_fixity'}
    batch = 1000
    mongodb = {'host': 'catalog.sd2e.org',
        'port': '27020', 'username': None,
        'password': None, 'replica_set': None}
