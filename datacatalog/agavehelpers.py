import re
import os
from requests import HTTPError
from datacatalog import settings
from datacatalog.stores import StorageSystem
from agavepy.agave import Agave, AgaveError
from tenacity import (retry, retry_if_exception_type,
                      stop_after_delay, wait_exponential)

from .stores import ManagedStores
from .utils import normalize

# TODO Factor the command runners into a class that handles the setup
# TODO Implement a more declarative form of support for these commands based on plugins
# FIXME listdir returns full paths, which is at odds with the POSIX implementation

class AgaveHelperError(AgaveError):
    pass

class AgaveHelperException(AgaveHelperError):
    pass

@retry(retry=retry_if_exception_type(AgaveError), reraise=True, stop=stop_after_delay(8), wait=wait_exponential(multiplier=2, max=64))
def ag_files_list(client, systemId, filePath, limit=50, offset=0):
    return client.files.list(systemId=systemId, filePath=filePath, limit=limit, offset=offset)

class AgaveHelper(object):
    """Uses an active API client to provide various utility functions
    """

    def __init__(self, client, storage_system=settings.STORAGE_SYSTEM):

        self._system = StorageSystem(storage_system, agave=client)
        self._client = client

    def get_storage_system(self, storage_system):
        if storage_system is not None:
            system = StorageSystem(storage_system, agave=self._client)
        else:
            system = self._system
        return system

    def mapped_posix_path(self, path, storage_system=None):
        """Resolve the absolute POSIX path for an Agave directory

        Args:
            path (str): Agave absolute path
            storage_system (str, optional): The storage system against which to resolve the POSIX path
        Returns:
            str: The path as a string
        """
        system = self.get_storage_system(storage_system)
        root_dir = system.root_dir
        normalized_path = normalize(path)
        return os.path.join(root_dir, normalized_path)

    def paths_to_agave_uris(self, filepaths, storage_system=None):
        """Transform a list of paths on a storage system to agave URI

        Args:
            filepaths (list): A list of agave storage system paths
            storage_system (str, optional): The storage system where these paths reside

        Returns:
            list: The paths in `agave://` format

        Warning:
            Existence of resources described by the URI list is not validated
        """
        system = self.get_storage_system(storage_system)
        uri_list = []
        for f in filepaths:
            uri_list.append(system.agave_path_uri(f))
        return uri_list

    def exists(self, path, storage_system=None):
        """Check if a path exists on an Agave storage resource

        Args:
            path (str): An Agave absolute path
            storage_system (str, optional): The storage system against which to resolve the POSIX path

        Raises:
            AgaveHelperError: The function has failed due an API error

        Returns:
            bool: Whether the path exists or not
        """
        system = self.get_storage_system(storage_system)
        try:
            if os.path.exists(self.mapped_posix_path(path, system)):
                return True
            else:
                try:
                    path_format = ag_files_list(self._client, filePath=path,
                                                systemId=system,
                                                limit=2)[0].get('format', None)
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
            raise AgaveHelperError('Function failed', exc)

    def dirname(self, path, storage_system=None):
        raise NotImplementedError()

    def isfile(self, path, storage_system=None):
        """Check if a path on an Agave storage resource is a file

        Args:
            path (str): An Agave absolute path
            storage_system (str, optional): The storage system against which to resolve the POSIX path

        Raises:
            AgaveHelperError: The function has failed due an API error

        Returns:
            bool: Whether the path is a file or not
        """
        system = self.get_storage_system(storage_system)
        try:
            if os.path.isfile(self.mapped_posix_path(path, system)):
                return True
            else:
                try:
                    path_format = ag_files_list(self._client, filePath=path,
                                                systemId=system,
                                                limit=2)[0].get('format', None)
                    if path_format != 'folder':
                        return True
                    else:
                        return False
                except Exception as exc:
                    raise AgaveHelperError('Function failed', exc)
        except AgaveHelperError as aexc:
            raise NotImplementedError(aexc)

    def isdir(self, path, storage_system=None):
        """Check if a path on an Agave storage resource is a directory

        Args:
            path (str): An Agave absolute path
            storage_system (str, optional): The storage system against which to resolve the POSIX path

        Raises:
            AgaveHelperError: The function has failed due an API error

        Returns:
            bool: Whether the path is a directory or not
        """
        system = self.get_storage_system(storage_system)
        try:
            if os.path.isdir(self.mapped_posix_path(path, system)):
                return True
            else:
                try:
                    path_format = ag_files_list(self._client, filePath=path,
                                                systemId=system,
                                                limit=2)[0].get('format', None)
                    if path_format == 'folder':
                        return True
                    else:
                        return False
                except Exception as exc:
                    raise AgaveHelperError('Function failed', exc)
        except AgaveHelperError as aexc:
            raise NotImplementedError(aexc)

    def islink(self, path, storage_system=None):
        raise NotImplementedError()

    def listdir(self, path, recurse, storage_system=None, directories=True):
        """Get the contents of a directory on an Agave storage resource

        Args:
            path (str): An Agave absolute path to directory
            storage_system (str, optional): The storage system where `path` is found
            directories (bool, optional): Whether to include directories in response

        Returns:
            list: Directory contents as a list of strings
        """
        system = self.get_storage_system(storage_system)
        dirlisting = list()
        try:
            dirlisting = self.listdir_agave_posix(path, recurse, system, directories)
            raise SystemError(dirlisting)
        except Exception:
            dirlisting = self.listdir_agave_native(path, recurse, system, directories)

        # Ensure listing is non-redundant
        # FIXME - figure out why there are redundant entries
        return list(set(dirlisting))

    def listdir_agave_posix(self, path, recurse=True, storage_system=None, directories=True):
        system = self.get_storage_system(storage_system)
        prefix = system.root_dir
        path = os.path.join(prefix, normalize(path))
        listing = list()
        files = list()
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        if directories is True:
            listing = [l.replace(prefix, '') for l in listing]
        else:
            listing = [l.replace(prefix, '')
                       for l in listing if not os.path.isdir(l)]
        return listing

    def listdir_agave_lustre(self, path, recurse=True, storage_system=None, directories=True):
        raise NotImplementedError(
            'Lustre support is not implemented. Consider using listdir_agave_posix().')

    def listdir_agave_native(self, path, recurse, storage_system=None, directories=True, current_listing=[]):
        system = self.get_storage_system(storage_system)
        pagesize = system.page_size
        listing = current_listing
        keeplisting = True
        skip = 0

        while keeplisting:
            sublist = ag_files_list(self._client, systemId=storage_system,
                                    filePath=path, limit=pagesize, offset=skip)
            # sublist = self._client.files.list(
            #     systemId=storage_system, filePath=path, limit=pagesize, offset=skip)
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
        listing.sort()
        return listing

    def delete(self, filePath, systemId):
        self._client.files.delete(filePath=filePath, systemId=systemId)

    def mkdir(self, dirName, systemId,
              basePath='/', sync=False, timeOut=60):
        """
        Creates a directory dirName on a storage system at basePath

        Like mkdir -p this is imdepotent. It will create the child path
        tree so long as paths are specified correctly, but will do
        nothing if all directories are already in place.
        """
        try:
            self._client.files.manage(systemId=systemId,
                                      body={'action': 'mkdir', 'path': dirName},
                                      filePath=basePath)
        except HTTPError as h:
            http_err_resp = process_agave_httperror(h)
            raise Exception(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unable to mkdir {} at {}/{}: {}".format(
                    dirName, systemId, basePath, e))
        return True

def from_agave_uri(uri=None, validate=False):
    """Partition an Agave storage URI into its components

    Args:
        uri (str): An agave-canonical files URI
        validate (bool, optional): Whether to validate the URL using an API call

    Raises:
        AgaveError: Occurs when invalid URI is passed

    Returns:
        tuple: Three strings are returned: storageSystem, directoryPath, and fileName
    """
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

def process_agave_httperror(http_error_object):

    h = http_error_object
    # extract HTTP response code
    code = -1
    try:
        code = h.response.status_code
        assert isinstance(code, int)
    except Exception:
        # we have no idea what the hell happened
        code = 418

    # extract HTTP reason
    reason = 'UNKNOWN ERROR'
    try:
        reason = h.response.reason
    except Exception:
        pass

    return reason
