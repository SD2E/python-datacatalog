# TODO: Load this in from a specific, write-restricted collection in database
import os
from .agave import AgaveSystems

__all__ = ['STORES', 'level_to_config_attr',
           'level_to_posix_path', 'store_to_posix_path']

STORES = {
    'uploads': {
        'prefix': 'uploads/',
        'level': '0',
        'storage_system': 'data-sd2e-community',
        'jupyter_dir': '\{User\}/tree/sd2e-community',
        'database': 'catalog',
        'fixity_collection': 'datafiles',
        'metadata_collection': 'files'
    },
    'products': {
        'prefix': 'products/',
        'level': '1',
        'storage_system': 'data-sd2e-community',
        'jupyter_dir': '\{User\}/tree/sd2e-community',
        'database': 'catalog',
        'fixity_collection': 'datafiles',
        'metadata_collection': 'files'
    },
    'reference': {
        'prefix': 'reference/',
        'level': 'Reference',
        'storage_system': 'data-sd2e-community',
        'jupyter_dir': '\{User\}/tree/sd2e-community',
        'database': 'catalog',
        'fixity_collection': 'datafiles',
        'metadata_collection': 'files'
    }
}

def level_to_config_attr(level, cattr):
    try:
        for store, config in STORES.items():
            if str(level) == config['level']:
                return config[cattr]
    except KeyError:
        raise KeyError('{} was not recognized as a config attribute'.format(cattr))
    raise ValueError('{} was not recognized as a level'.format(level))

def level_to_posix_path(level):
    agave_sys = level_to_config_attr(level, 'storage_system')
    try:
        return AgaveSystems.storage.get(agave_sys, {}).get('root_dir', '/tmp')
    except:
        raise ValueError('{} did not resolve to a POSIX root directory'.format(level))

def store_to_posix_path(store):
    agave_sys = STORES[store]['storage_system']
    try:
        return AgaveSystems.storage.get(agave_sys, {}).get('root_dir', '/tmp')
    except:
        raise ValueError(
            '{} did not resolve to a POSIX root directory'.format(store))
