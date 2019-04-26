import inspect
import json
import os
from datacatalog.extensible import ExtensibleAttrDict
from ..utils import normalize
from .exceptions import ManagedStoreError

class StorageSystem(str):
    """Abstract representation of an Agave API storage system
    """
    MEMBERS = [('data-sd2e-community', 'Project-level data'),
               ('data-sd2e-app-assets', 'Managed public system'),
               ('data-sd2e-projects-users', 'Managed user data')]

    def __new__(cls, value, agave=None):
        value = str(value).lower()
        if value not in dict(cls.MEMBERS):
            raise ValueError('"{}" is not a known {}'.format(value, cls.__name__))
        return str.__new__(cls, value)

    def __init__(self, name, local=True, agave=None):
        super().__init__()
        setattr(self, '_cache', None)
        setattr(self, '_agave', agave)
        if local:
            modfile = inspect.getfile(self.__class__)
            storefile = os.path.join(os.path.dirname(modfile), 'systems.json')
            # load in mappings.json
            # array of system defs, mirroring response from agave.systems.list()
            contents = json.load(open(storefile, 'r'))
            for system in contents:
                if system.get('id') == self:
                    setattr(self, '_cache', ExtensibleAttrDict(system))
                    break
        if self._cache is None:
            raise ManagedStoreError('Failed to initialize a StorageSystem')
        # TODO - Add ability to look up attributes of a system given an Agave client

    @property
    def description(self):
        return self._cache.description

    @property
    def home_dir(self):
        return self._cache.storage['homeDir']

    @property
    def name(self):
        return self._cache.name

    @property
    def owner(self):
        return self._cache.owner

    @property
    def page_size(self):
        return 50

    @property
    def root_dir(self):
        return self._cache.storage['rootDir']

    @property
    def ssh_host(self):
        if self._cache.storage['protocol'] == 'SFTP':
            return self._cache.storage['host'] + ':' + str(self._cache.storage['port'])
        else:
            raise ManagedStoreError('{} is not an SSH-based system'.format(self.name))

    @property
    def system_id(self):
        return self._cache.id

    @classmethod
    def agave_path_uri(self, path):
        return 'agave://' + self + normalize(path)
