import inspect
import json
import os
from datacatalog import settings
from datacatalog.extensible import ExtensibleAttrDict
from .agave import StorageSystem
from .exceptions import ManagedStoreError
from .level import Level
from ..utils import normalize, normpath

class ManagedStore(ExtensibleAttrDict):
    """Representation of a Data Catalog managed store
    """
    BLACKLIST = ['/usr', '/bin', '/var', '/tmp', '/root', '/lib']

    def __init__(self,
                 prefix=None,
                 level='User',
                 storage_system=settings.STORAGE_SYSTEM,
                 **kwargs):
        super().__init__()
        for b in self.BLACKLIST:
            if prefix.startswith(b):
                raise ValueError('Prefix not allowed')
        setattr(self, 'prefix', prefix)
        setattr(self, 'level', Level(level))
        setattr(self, 'storage_system', StorageSystem(storage_system))

class ManagedStores(object):
    """Representation of all Data Catalog managed stores
    """
    STORES = [
        {'level': '0', 'prefix': '/uploads',
         'storage_system': settings.STORAGE_SYSTEM,
         'manager': settings.TACC_MANAGER_ACCOUNT,
         'database': settings.MONGODB_DATABASE},
        {'level': '1', 'prefix': '/products',
         'storage_system': settings.STORAGE_SYSTEM,
         'manager': settings.TACC_MANAGER_ACCOUNT,
         'database': settings.MONGODB_DATABASE},
        {'level': '2', 'prefix': '/products',
         'storage_system': settings.STORAGE_SYSTEM,
         'manager': settings.TACC_MANAGER_ACCOUNT,
         'database': settings.MONGODB_DATABASE},
        {'level': '3', 'prefix': '/products',
         'storage_system': settings.STORAGE_SYSTEM,
         'manager': settings.TACC_MANAGER_ACCOUNT,
         'database': settings.MONGODB_DATABASE},
        {'level': 'Reference', 'prefix': '/reference',
         'storage_system': settings.STORAGE_SYSTEM,
         'manager': settings.TACC_MANAGER_ACCOUNT,
         'database': settings.MONGODB_DATABASE},
        {'level': 'User', 'prefix': '/sample',
         'storage_system': settings.STORAGE_SYSTEM,
         'manager': settings.TACC_MANAGER_ACCOUNT,
         'database': settings.MONGODB_DATABASE}]

    @classmethod
    def stores(cls):
        return cls.STORES

    @classmethod
    def prefixes_for_level(cls, level):
        prefixes = list()
        for st in cls.stores():
            if st.get('level') == Level(level):
                prefixes.append(st.get('prefix'))
        if len(prefixes) > 0:
            return sorted(prefixes)
        else:
            raise ManagedStoreError('Cannot resolve prefixes from level')

    @classmethod
    def store_for_level(cls, level):
        for st in cls.stores():
            if st.get('level') == Level(level):
                return StorageSystem(st.get('storage_system'))
        raise ManagedStoreError('Cannot resolve store to level')

    @classmethod
    def store_for_prefix(cls, prefix):
        for st in cls.stores():
            if st.get('prefix') == prefix:
                return StorageSystem(st.get('storage_system'))
        raise ManagedStoreError('Cannot resolve store to prefix')

    @classmethod
    def levels_for_prefix(cls, prefix):
        levels = list()
        for st in cls.stores():
            if st.get('prefix') == prefix:
                levels.append(Level(st.get('level')))
        if len(levels) > 0:
            return sorted(levels)
        else:
            raise ManagedStoreError('Cannot resolve levels from prefix')

    @classmethod
    def levels_for_filepath(cls, filepath):
        levels = list()
        for st in cls.stores():
            if filepath.startswith(st.get('prefix')):
                levels.append(Level(st.get('level')))
        if len(levels) > 0:
            return sorted(levels)
        else:
            raise ManagedStoreError('Cannot resolve levels from prefix')

    @classmethod
    def stores_for_filepath(cls, filepath):
        stores = list()
        for st in cls.stores():
            if filepath.startswith(st.get('prefix')):
                stores.append(StorageSystem(st.get('storage_system')))
        if len(stores) > 0:
            return sorted(stores)
        else:
            raise ManagedStoreError('Cannot resolve store from prefix')

def abspath(filepath, validate=False):
    """Absolute path on host filesystem"""
    normalized_path = normalize(filepath)
    normed_path = normpath(filepath)
    if os.environ.get('DEBUG_STORES_NATIVE_PREFIX', None):
        root_dir = os.environ.get('DEBUG_STORES_NATIVE_PREFIX', None)
    else:
        root_dir = ManagedStores.stores_for_filepath(normed_path)[0].root_dir
    return os.path.join(root_dir, normalized_path)
