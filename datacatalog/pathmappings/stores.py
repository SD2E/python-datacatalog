import re
import os
from .levels import level_for_filepath, prefix_for_level, store_for_level

DEFAULT_STORAGE_SYSTEM = 'data-sd2e-community'
DEFAULT_PATH_TYPE = 'native'

STORES = {'data-sd2e-community': {
    'native': '/work/projects/SD2E-Community/prod/data',
    'jupyter': '/home/jupyter/sd2e-community',
    'jupyterhub': '\{User\}/tree/sd2e-community',
    'agave': '/'}
}

def normalize(filepath):
    # Prefixes are terminated with '/' to indicate they are directories. Thus,
    # to avoid double-slashes, all paths should have leading slashes trimmed.
    if filepath.startswith('/'):
        filepath = filepath[1:]
    return filepath

def normpath(filepath):
    fp = re.sub('^(/)+', '/', filepath)
    return os.path.normpath(fp)

def abspath(filepath, validate=False):
    # Resolve the native POSIX path for a given managed file path
    normalized_filepath = normalize(filepath)
    if os.environ.get('DEBUG_STORES_NATIVE_PREFIX') is not None:
        store_pfx = os.environ.get('DEBUG_STORES_NATIVE_PREFIX')
    else:
        store_pfx = root_prefix(filepath, path_type='native')
    absolute_path = os.path.join(store_pfx, normalized_filepath)
    if validate:
        if not os.path.exists(absolute_path):
            raise OSError('File {} not found'.format(absolute_path))
    return absolute_path

def relativize(filepath, storage_system=DEFAULT_STORAGE_SYSTEM, path_type=DEFAULT_PATH_TYPE):
    if storage_system not in list(STORES.keys()):
        raise KeyError('Unrecognized storage system {}'.format(storage_system))
    if path_type not in list(STORES[storage_system].keys()):
        raise KeyError('Unrecognized path_type: {}'.format(path_type))
    root_prefix = STORES[storage_system][path_type]
    rel_filepath = normalize(filepath.replace(root_prefix, ''))
    return rel_filepath

def root_prefix(filepath, path_type=DEFAULT_PATH_TYPE):
    # Resolve the root prefix for a given path for any known type
    normalized_filepath = normalize(filepath)
    lev = level_for_filepath(normalized_filepath)
    store = store_for_level(lev)
    if path_type not in list(STORES[store].keys()):
        raise KeyError('Unrecognized path_type: {}'.format(path_type))
    store_pfx = STORES.get(store).get(path_type)
    return store_pfx
