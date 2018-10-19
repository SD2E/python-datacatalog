from . import MAPPINGS

def prefix_for_level(level):
    try:
        return MAPPINGS.get(str(level))
    except KeyError:
        raise KeyError('Processing level {} is not known'.format(level))

def level_for_prefix(prefix):
    for lev, pfx in MAPPINGS.items():
        if prefix == pfx:
            return lev
    raise KeyError('Prefix {} does not map to a processing level'.format(prefix))

def level_for_filepath(filepath):
    if not filepath.startswith('/'):
        filepath = '/' + filepath
    for lev, pfx in MAPPINGS.items():
        if filepath.startswith(pfx):
            return lev
    raise KeyError('Path does not map to a known prefix')
