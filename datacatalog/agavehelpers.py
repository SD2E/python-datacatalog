
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *

import re
import os
from requests import HTTPError
from agavepy.agave import Agave, AgaveError
from .constants import AgaveSystems
from .configs import CatalogStore

# TODO Factor the command runners into a class that handles the setup
# TODO Implement a more declarative form of support for these commands based on plugins
# FIXME listdir returns full paths, which is at odds with the POSIX implementation

DEF_STORAGE_SYSTEM = 'data-sd2e-community'


class AgaveHelperException(Exception):
    pass


class AgaveHelper(object):
    def __init__(self, client):
        self.STORAGE_SYSTEM = os.environ.get(
            'CATALOG_STORAGE_SYSTEM', CatalogStore.agave_storage_system)
        self.STORAGE_PREFIX = os.environ.get(
            'CATALOG_ROOT_DIR', AgaveSystems.storage[DEF_STORAGE_SYSTEM]['root_dir'])
        self.STORAGE_PAGESIZE = os.environ.get(
            'CATALOG_FILES_API_PAGESIZE', AgaveSystems.storage[DEF_STORAGE_SYSTEM]['pagesize'])
        self.client = client

    def mapped_posix_path(self, path, storage_system=None):
        # if storage_system is None:
        #     storage_system = self.STORAGE_SYSTEM
        #     prefix = AgaveSystems.storage[storage_system]['root_dir']
        # else:
        prefix = self.STORAGE_PREFIX
        if path.startswith('/'):
            path = path[1:]
        return os.path.join(prefix, path)

    def paths_to_agave_uris(self, filepaths, storage_system=None):
        """Transform a list of absolute paths on a storage system to agave-canonical URIs"""
        if storage_system is None:
            storage_system = self.STORAGE_SYSTEM
        uri_list = []
        for f in filepaths:
            if f.startswith('/'):
                f = f[1:]
            uri_list.append(os.path.join('agave://', storage_system, f))
        return uri_list

    def exists(self, path, storage_system=None):
        if storage_system is None:
            storage_system = self.STORAGE_SYSTEM
        prefix = self.STORAGE_PREFIX
        try:
            if os.path.exists(self.mapped_posix_path(path, storage_system)):
                return True
            else:
                try:
                    path_format = self.client.files.list(
                        filePath=path, systemId=storage_system, limit=2)[0].get('format', None)
                    if path_format != 'folder':
                        return True
                    else:
                        return False
                except HTTPError as herr:
                    if herr.response.status_code == 404:
                        return False
                    else:
                        raise HTTPError(herr)
        except Exception as exc:
            raise AgaveHelperException('Function failed', exc)

    def dirname(self, path, storage_system=None):
        raise NotImplementedError()

    def isfile(self, path, storage_system=None):
        if storage_system is None:
            storage_system = self.STORAGE_SYSTEM
        prefix = self.STORAGE_PREFIX
        try:
            if os.path.isfile(self.mapped_posix_path(path, storage_system)):
                return True
            else:
                try:
                    path_format = self.client.files.list(
                        filePath=path, systemId=storage_system, limit=2)[0].get('format', None)
                    if path_format != 'folder':
                        return True
                    else:
                        return False
                except Exception as exc:
                    raise AgaveHelperException('Function failed', exc)
        except AgaveHelperException as aexc:
            raise NotImplementedError(aexc)

    def isdir(self, path, storage_system=None):
        if storage_system is None:
            storage_system = self.STORAGE_SYSTEM
        prefix = self.STORAGE_PREFIX
        try:
            if os.path.isdir(self.mapped_posix_path(path, storage_system)):
                return True
            else:
                try:
                    path_format = self.client.files.list(
                        filePath=path, systemId=storage_system, limit=2)[0].get('format', None)
                    if path_format == 'folder':
                        return True
                    else:
                        return False
                except Exception as exc:
                    raise AgaveHelperException('Function failed', exc)
        except AgaveHelperException as aexc:
            raise NotImplementedError(aexc)

    def islink(self, path, storage_system=None):
        raise NotImplementedError()

    def listdir(self, path, recurse, storage_system=None, directories=True):
        """Return a list containing the names of the entries in the directory
        given by path.

        Gets a directory listing from the default storage system unless specified.
        For performance, direct POSIX is tried first, then API if that fails.

        Parameters:
        path:str - storage system-absolute path to list
        Arguments:
        storage_system:str - non-default Agave storage system
        Returns:
        listing:list - all directory contents
        """
        if storage_system is None:
            storage_system = self.STORAGE_SYSTEM
        try:
            return self.listdir_agave_posix(path, recurse, storage_system, directories)
        except Exception:
            return self.listdir_agave_native(path, recurse, storage_system, directories)

    def listdir_agave_posix(self, path, recurse=True, storage_system=None, directories=True, current_listing=[]):
        if storage_system is None:
            storage_system = self.STORAGE_SYSTEM
        prefix = self.STORAGE_PREFIX
        listing = current_listing

        if path.startswith('/'):
            path = path[1:]
        full_path = os.path.join(prefix, path)
        for f in os.listdir(full_path):
            af = os.path.join(full_path, f)
            listing.append(af)
            if os.path.isdir(af) and recurse is True:
                self.listdir_agave_posix(
                    path + '/' + f, recurse, storage_system, directories, current_listing=listing)
        if directories is True:
            listing = [l.replace(prefix, '') for l in listing]
        else:
            listing = [l.replace(prefix, '')
                       for l in listing if not os.path.isdir(l)]
        return listing

    def listdir_agave_lustre(self, path, recurse=True, storage_system=None, directories=True, current_listing=[]):
        raise NotImplementedError(
            'Lustre support is not implemented. Consider using listdir_agave_posix().')

    def listdir_agave_native(self, path, recurse, storage_system=None, directories=True, current_listing=[]):
        if storage_system is None:
            storage_system = self.STORAGE_SYSTEM
        pagesize = self.STORAGE_PAGESIZE
        listing = current_listing
        keeplisting = True
        skip = 0

        while keeplisting:
            sublist = self.client.files.list(
                systemId=storage_system, filePath=path, limit=pagesize, offset=skip)
            skip = skip + pagesize
            if len(sublist) < pagesize:
                keeplisting = False
            for f in sublist:
                if f['name'] != '.':
                    if f['format'] != 'folder' or directories is True:
                        listing.append(f['path'])
                    if f['format'] == 'folder' and recurse is True:
                        self.listdir_agave_native(
                            f['path'], recurse, storage_system, directories, current_listing=listing)
        return sorted(listing)

def from_agave_uri(uri=None, Validate=False):
    """Parse an Agave URI into a tuple (systemId, directoryPath, fileName)
    Validation that it points to a real resource is not implemented. The
    same caveats about validation apply here as in to_agave_uri()"""
    systemId = None
    dirPath = None
    fileName = None
    proto = re.compile(r'agave:\/\/(.*)$')
    if uri is None:
        raise AgaveError("URI cannot be empty")
    resourcepath = proto.search(uri)
    if resourcepath is None:
        raise AgaveError("Unable resolve URI")
    resourcepath = resourcepath.group(1)
    firstSlash = resourcepath.find('/')
    if firstSlash is -1:
        raise AgaveError("Unable to resolve systemId")
    try:
        systemId = resourcepath[0:firstSlash]
        origDirPath = resourcepath[firstSlash + 1:]
        dirPath = '/' + os.path.dirname(origDirPath)
        fileName = os.path.basename(origDirPath)
        return (systemId, dirPath, fileName)
    except Exception as e:
        raise AgaveError(
            "Error resolving directory path or file name: {}".format(e))
