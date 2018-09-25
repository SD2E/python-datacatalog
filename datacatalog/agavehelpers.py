
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *

import re
import os
from agavepy.agave import Agave, AgaveError
from .constants import AgaveSystems
from .configs import CatalogStore

STORAGE_SYSTEM = os.environ.get('CATALOG_STORAGE_SYSTEM', CatalogStore.agave_storage_system)
STORAGE_PREFIX = os.environ.get('CATALOG_STORAGE_PREFIX', AgaveSystems.storage[STORAGE_SYSTEM]['root_dir'])
STORAGE_PAGESIZE = os.environ.get('CATALOG_STORAGE_PAGESIZE', AgaveSystems.storage[STORAGE_SYSTEM]['pagesize'])

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


def paths_to_agave_uris(filepaths, storage_system=STORAGE_SYSTEM):
    """Transform a list of absolute paths on a storage system to agave-canonical URIs"""
    uri_list = []
    for f in filepaths:
        if f.startswith('/'):
            f = f[1:]
        uri_list.append(os.path.join('agave://', storage_system, f))
    return uri_list

def listdir(path, recurse=True, storage_system=STORAGE_SYSTEM, agave_client=None, directories=True):
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
    try:
        return __listdir_agave_posix(path, recurse, storage_system, directories)
    except Exception:
        if agave_client is None:
            agave_client = Agave.restore()
        return __listdir_agave_native(path, recurse, storage_system, agave_client, directories)


def __listdir_agave_posix(path, recurse, storage_system, directories, current_listing=[]):
    prefix = STORAGE_PREFIX
    listing = current_listing
    if path.startswith('/'):
        path = path[1:]
    full_path = os.path.join(prefix, path)
    for f in os.listdir(full_path):
        af = os.path.join(full_path, f)
        listing.append(af)
        if os.path.isdir(af) and recurse is True:
            __listdir_agave_posix(path + '/' + f, recurse, storage_system, directories, current_listing=listing)
    if directories is True:
        listing = [l.replace(prefix, '') for l in listing]
    else:
        listing = [l.replace(prefix, '') for l in listing if not os.path.isdir(l)]
    return listing


def __listdir_agave_native(path, recurse, storage_system, agave_client, directories=True, current_listing=[]):
    pagesize = STORAGE_PAGESIZE
    listing = current_listing
    keeplisting = True
    skip = 0

    while keeplisting:
        sublist = agave_client.files.list(systemId=storage_system, filePath=path, limit=pagesize, offset=skip)
        skip = skip + pagesize
        if len(sublist) < pagesize:
            keeplisting = False
        for f in sublist:
            if f['name'] != '.':
                if f['format'] != 'folder' or directories is True:
                    listing.append(f['path'])
                if f['format'] == 'folder' and recurse is True:
                    __listdir_agave_native(
                        f['path'], recurse, storage_system, agave_client, directories, current_listing=listing)
    return sorted(listing)

# def __listdir_agave_native(path, recurse, storage_system, agave_client, directories=True, current_listing=[]):
#     pagesize = STORAGE_PAGESIZE
#     listing = current_listing
#     keeplisting = True
#     skip = 0

#     while keeplisting:
#         sublist = agave_client.files.list(systemId=storage_system,
#             filePath=path, limit=pagesize, offset=skip)
#         skip = skip + pagesize
#         if len(sublist) < pagesize:
#             keeplisting = False
#         for f in sublist:
#             if f['name'] != '.':
#                 if f['format'] != 'folder' or directories is True:
#                     listing.append(f['path'])
#                 if f['format'] == 'folder' and recurse is True:
#                     __listdir_agave_native(
#                         f['path'], recurse, storage_system, agave_client, directories, current_listing=listing)
#     return sorted(listing)
