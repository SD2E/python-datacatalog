import os
from datacatalog import settings

__all__ = ['cache_directory', 'init_cache', 'clear_cache',
           'SLOW_CACHE_WARN_THRESHOLD', 'MAX_CACHE_AGE_SECONDS',
           'CACHE_FILE_SUFFIX']

CACHE_DIR_NAME = '.pjs-cache'
CACHE_FILE_SUFFIX = '.pickle'
MAX_CACHE_AGE_SECONDS = settings.PJS_CACHE_MAX_AGE
SLOW_CACHE_WARN_THRESHOLD = 0.95

def cache_directory(cache_dir=None):
    """Resolves location of PJSO cache directory
    """
    cdir = '.'

    if cache_dir is None:
        # Default to $HOME/.pjs-cache
        if settings.PJS_CACHE_DIR is None or settings.PJS_CACHE_DIR == '':
            cdir = os.path.join(os.path.expanduser('~'), CACHE_DIR_NAME)
        else:
            # But allow override from os.environ
            cdir = settings.PJS_CACHE_DIR
    else:
        cdir = cache_dir

    init_cache(cache_dir=cdir)
    return cdir

def init_cache(cache_dir=None):
    """Initializes the PJSO object cache
    """
    if cache_dir is None:
        cache_dir = cache_directory(cache_dir)
    try:
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    except OSError:
        return None

def clear_cache(cache_dir=None):
    """Clears all cached PJSO objects
    """
    if cache_dir is None:
        cache_dir = cache_directory(cache_dir)
    try:
        for cf in os.listdir(cache_dir):
            if os.path.isfile(cf) and cf.endswith(CACHE_FILE_SUFFIX):
                os.unlink(cf)
    except Exception:
        raise

