import inspect
import json
import os
from datacatalog import settings
from datacatalog.extensible import ExtensibleAttrDict
from .agave import StorageSystem
from .level import Level
from ..utils import normalize

class PathMapping(ExtensibleAttrDict):
    """Representation of a managed store with levels
    """

    def __init__(self, system_id, path_mapping, agave=None):
        super().__init__()
        setattr(self, '_system', StorageSystem(system_id, agave=agave))
        setattr(self, '_mapping', path_mapping)

    @property
    def hpc_path(self):
        """Path on TACC CLI systems
        """
        return self._system.root_dir

    def hpc_path_uri(self, username='<username>'):
        """SFTP URI

        Implements RFC-3986 (expired) encoding of an SFTP URI
        """
        return 'sftp://' + username + '@' + self._system.ssh_host + self.hpc_path

    @property
    def agave_path(self):
        """Agave absolute path
        """
        return self._system.home_dir

    @property
    def agave_path_uri(self):
        """Agave files URI
        """
        url = settings.TACC_API_SERVER + self._system + self.agave_path
        return url

    @property
    def jupyter_path(self):
        """Path within Jupyter notebooks
        """
        return self._mapping.get('jupyter')

    @property
    def jupyterhub_path(self):
        """User-agnostic path in JupyterHub application
        """
        return self._mapping.get('jupyterhub')

    @property
    def jupyterhub_path_uri(self):
        """JupyterHub application URI
        """
        url = settings.TACC_JUPYTER_SERVER + self.jupyterhub_path
        return url

class PathMappings(object):
    _maps = list()

    """Maps managed stores to levels and physical file paths across platforms
    """
    @classmethod
    def map(cls, system_id, agave=None):
        mod = inspect.getmodule(cls)
        modfile = inspect.getfile(mod)
        storefile = os.path.join(os.path.dirname(modfile), 'mappings.json')
        contents = json.load(open(storefile, 'r'))
        for k, v in contents.items():
            if k == system_id:
                m = PathMapping(k, v, agave=agave)
                if m not in cls._maps:
                    cls._maps.append(m)
                return m
