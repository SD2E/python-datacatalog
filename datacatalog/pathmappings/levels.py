import os

LEVELS = {'0': {'prefix': '/uploads/', 'store': 'data-sd2e-community'},
          '1': {'prefix': '/products/', 'store': 'data-sd2e-community'},
          '2': {'prefix': '/products/', 'store': 'data-sd2e-community'},
          'Reference': {'prefix': '/reference/', 'store': 'data-sd2e-community'}}

def prefix_for_level(level):
    try:
        return LEVELS.get(str(level)).get('prefix')
    except KeyError:
        if os.environ.get('DEBUG_STORES_NATIVE_PREFIX') is not None:
            return '0'
        else:
            raise KeyError('Processing level {} is not known'.format(level))

def store_for_level(level):
    try:
        return LEVELS.get(str(level)).get('store')
    except KeyError:
        raise KeyError('Processing level {} is not known'.format(level))

def level_for_prefix(prefix):
    for lev, props in LEVELS.items():
        if prefix == props['prefix']:
            return lev
    if os.environ.get('DEBUG_STORES_NATIVE_PREFIX') is not None:
        return '0'
    else:
        raise KeyError('Prefix {} does not map to a processing level'.format(prefix))

def level_for_filepath(filepath):
    if not filepath.startswith('/'):
        filepath = '/' + filepath
    for lev, props in LEVELS.items():
        if filepath.startswith(props['prefix']):
            return lev
    if os.environ.get('DEBUG_STORES_NATIVE_PREFIX') is not None:
        return '0'
    else:
        return 'User'
        # raise KeyError('Path does not map to a known prefix')
