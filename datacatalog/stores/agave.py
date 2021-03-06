import inspect
import json
import os
import re
from functools import lru_cache
from datacatalog.hashable import picklecache, jsoncache
from datacatalog.extensible import ExtensibleAttrDict
from datacatalog import settings

from ..utils import normalize, normpath
from .exceptions import ManagedStoreError

COMMUNITY_TYPE = 'community'
PROJECT_TYPE = 'project'
PUBLIC_TYPE = 'public'
SHARE_TYPE = 'share'
WORK_TYPE = 'work'

SYSTEM_TYPES = (COMMUNITY_TYPE, PUBLIC_TYPE, SHARE_TYPE, PROJECT_TYPE, WORK_TYPE)
TYPE_RES = {COMMUNITY_TYPE: re.compile('data-(sd2e-community)'),
            PUBLIC_TYPE: re.compile('data-sd2e-projects-(users)'),
            SHARE_TYPE: re.compile('data-sd2e-projects.([-.a-zA-Z0-9]{4,})'),
            PROJECT_TYPE: re.compile('data-projects-([-.a-zA-Z0-9]{4,})'),
            WORK_TYPE: re.compile('data-tacc-work-([a-zA-Z0-9]{3,8})')
            }
JUPYTER_BASE = '/user/{User}/tree'

class StorageSystem(str):
    """Abstract representation of an Agave API storage system
    """
    def __new__(cls, value, agave=None):
        value = str(value).lower()
        # if value not in dict(cls.MEMBERS):
        #     raise ValueError('"{}" is not a known {}'.format(value, cls.__name__))
        return str.__new__(cls, value)

    def __init__(self, name, local=True, agave=None):
        super().__init__()
        self.set_type_and_name(permissive=False)
        assert agave is not None, 'StorageSystem requires a valid API client'
        setattr(self, 'client', agave)
        setattr(self, '_cache', self.get_system_record(permissive=False))

    def set_type_and_name(self, permissive=False):
        """Uses regular expressions to find type and short name for system
        """
        for t, r in TYPE_RES.items():
            rs = r.match(self)
            if rs:
                setattr(self, '_type', t)
                setattr(self, '_short_name', rs.group(1))
                return True
        if permissive is False:
            raise ManagedStoreError(
                'Unable to determine type/short name for {}'.format(self))

    @picklecache.mcache(lru_cache(maxsize=256))
    def get_system_record(self, permissive=False):
        modfile = inspect.getfile(self.__class__)
        storefile = os.path.join(os.path.dirname(modfile), 'systems.json')
        # load in mappings.json
        # array of system defs, mirroring response from agave.systems.list()
        contents = json.load(open(storefile, 'r'))
        for system in contents:
            # SHOULD THIS BE system.get('id') == name
            if system.get('id') == self:
                return ExtensibleAttrDict(system)
        try:
            sys = self.client.systems.get(systemId=self)
            return ExtensibleAttrDict(sys)
        except Exception as exc:
            raise ManagedStoreError(
                'Unable to fetch StorageSystem {} [{}]'.format(
                    self, str(exc)))

    @property
    def system_id(self):
        return self._cache.id

    @property
    def name(self):
        return self._cache.name

    @property
    def description(self):
        return self._cache.description
    @property
    def owner(self):
        return self._cache.owner

    @property
    def page_size(self):
        return 50

    @property
    def ssh_host(self):
        if self._cache.storage['protocol'] == 'SFTP':
            return self._cache.storage['host'] + ':' + str(self._cache.storage['port'])
        else:
            raise ManagedStoreError(
                '{} is not an SSH-based POSIX system'.format(self.name))


    @property
    def type(self):
        return self._type

    @property
    def short_name(self):
        return self._short_name

    @property
    def home_dir(self):
        return self._cache.storage['homeDir']

    @property
    def root_dir(self):
        return self._cache.storage['rootDir']

    def agave_dir(self, path):
        agave_base = self.root_dir + self.home_dir
        agave_dir = path.replace(agave_base, '/')
        agave_dir = re.sub('^/+', '/', agave_dir)
        return agave_dir

    @property
    def work_dir(self):
        return self.root_dir

    @property
    def hpc_dir(self):
        return self.work_dir

    @property
    def abaco_dir(self):
        return self.work_dir

    def _jupyter_user_base(self):
        return '/user/' + self.short_name + '/tree'

    @property
    def jupyter_dir(self):
        if self.type == COMMUNITY_TYPE:
            return os.path.join(JUPYTER_BASE, self._short_name)
        elif self.type == WORK_TYPE:
            return self._jupyter_user_base() + '/tacc-work'
        elif self.type == SHARE_TYPE:
            return os.path.join(JUPYTER_BASE, 'sd2e-projects', self.short_name)
        elif self.type == PROJECT_TYPE:
            return os.path.join(JUPYTER_BASE, 'sd2e-partners', self.short_name)
        elif self.type == PUBLIC_TYPE:
            # We do not allow any exposure of the Agave public system assets
            # via Jupyter, esp. because we use it to store application assets
            raise ManagedStoreError('{} is not available via Jupyter'.format(
                self.system_id))
        else:
            raise ManagedStoreError('Failed to resolve Jupyter path')

    @classmethod
    def agave_path_uri(self, path):
        return 'agave://' + self + normalize(path)

    @classmethod
    def jupyter_path_uri(self, path):
        return settings.TACC_JUPYTER_SERVER + path

def abspath(self, filepath, storage_system=None, agave=None, validate=False):
    """Resolve absolute path on host filesystem for an Agave path"""
    normalized_path = normalize(filepath)
    if os.environ.get('STORAGE_SYSTEM_PREFIX_OVERRIDE', None) is not None:
        root_dir = os.environ.get('STORAGE_SYSTEM_PREFIX_OVERRIDE')
    else:
        root_dir = StorageSystem(storage_system, agave=agave).root_dir
    return os.path.join(root_dir, normalized_path)
