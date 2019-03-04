import binascii
import datetime
import filetype
import hashlib
import xxhash
import os
import sys
from stat import S_ISREG
from pprint import pprint

from ...filetypes import infer_filetype
from ...stores import abspath
from ...utils import normalize, normpath
from .schema import FixityDocument, msec_precision

class FixityIndexer(object):
    """Captures fixed details for a given file"""
    CHECKSUM_BLOCKSIZE = 128000
    """Chunk size for computing checksum"""
    DEFAULT_SIZE = -1
    """Default size in bytes when it cannot be determined"""
    XXHASH32_SEED = 2573985330
    """Seed for xxHash 32-bit fingerprinting"""
    XXHASH64_SEED = 3759046909696704950
    """Seed for xxHash 64-bit fingerprinting"""

    __PARAMS = [('name', 'name', False, None),
                ('version', 'version', True, 0),
                ('type', 'type', True, None),
                ('created', 'created', True, None),
                ('modified', 'modified', True, None),
                ('size', 'size', True, None),
                ('checksum', 'checksum', True, None),
                ('fingerprint', 'fingerprint', True, None),
                ('uuid', 'uuid', False, None),
                ('child_of', 'child_of', False, []),
                ('generated_by', 'generated_by', False, [])]

    def __init__(self, abs_filename=None, schema={}, cache_stat=True,
                 block_size=CHECKSUM_BLOCKSIZE, **kwargs):
        self._cache_stat = cache_stat
        self._block_size = block_size
        self.name = kwargs.get('name')
        # set._abspath on filesystem if not passed in
        if abs_filename is not None:
            self._abspath = abs_filename
        else:
            self._abspath = abspath(self.name)
        # We have specific rules about what constitutes an update
        self._updated = False
        # This holds a cached version of the os.path.stat() tuple, saving
        # three of the four individual stat() calls for get_created,
        # get_modified, and get_size, and is_file!
        if self._cache_stat:
            setattr(self, '_stat', os.stat(self._abspath))
            setattr(self, '_is_file', S_ISREG(self._stat.st_mode))
        else:
            setattr(self, '_is_file', os.path.isfile(self._abspath))

        for key, attr, init, default in self.__PARAMS:
            value = kwargs.get(key, default)
            setattr(self, attr, value)

    def sync(self):
        """Fetch latest values for indexing target"""
        setattr(self, '_updated', False)
        if self._is_file is True:
            for key, attr, func, default in self.__PARAMS:
                if func:
                    addressable_method = getattr(self, 'get_' + attr)
                    old_value = getattr(self, attr, None)
                    try:
                        new_value = addressable_method(self._abspath)
                        if new_value != old_value:
                            setattr(self, '_updated', True)
                        setattr(self, attr, new_value)
                    except Exception as exc:
                        pprint(exc)

        # print('sync.attr:value {}:{}'.format(attr, new_value))
        if self._updated is True:
            vers = self.get_version()
            vers = vers + 1
            setattr(self, 'version', vers)
        return self

    def to_dict(self):
        """Render fixity record as a dictionary

        Returns:
            dict: Representation of this fixity record
        """
        my_dict = dict()
        for key, attr, init, default in self.__PARAMS:
            my_dict[key] = getattr(self, attr)
        return my_dict

    def updated(self):
        """Helper to manage ``updated`` state
        """
        return getattr(self, '_updated', False)

    def get_checksum(self, file, algorithm='sha256'):
        """Compute checksum for indexing target

        Args:
            file (str): Absolute path to the file
            algorithm (str, optional): Checksum algorithm to use

        Returns:
            str: Hexadecimal checksum for the file
        """
        cksum = self.__checksum_sha256(file)
        return cksum

    def get_version(self, file=None):
        return getattr(self, 'version', 0)

    def get_fingerprint(self, file, algorithm='xxh64'):
        """Compute fast fingerprint for indexing target

        Args:
            file (str): Absolute path to the file
            algorithm (str, optional): Fingerprint algorithm to use

        Returns:
            str: Hexadecimal checksum for the file
        """
        cksum = self.checksum_xxhash(file)
        return cksum

    def get_created(self, file):
        """Returns (apparent) file creation time.

        Args:
            file (str): Absolute path to the file

        Returns:
            datetime.datetime: The file's ``ctime``

        Note:
            Only msec precision is supported, a deficiency inherited from BSON
        """
        if getattr(self, 'created') is not None:
            return getattr(self, 'created')
        else:
            stat_cache = getattr(self, '_stat', None)
            if stat_cache is not None:
                t = stat_cache.st_ctime
            else:
                t = os.path.getmtime(file)
            return msec_precision(datetime.datetime.fromtimestamp(t))

    def get_size(self, file):
        """Returns size in bytes for files (or DEFAULT_SIZE if unknown)
        """
        gs = self.DEFAULT_SIZE
        stat_cache = getattr(self, '_stat', None)
        if stat_cache is not None:
            return stat_cache.st_size
        else:
            gs = os.path.getsize(file)
            if gs is None:
                raise OSError(
                    'Failed to get size of {}'.format(file))
        return gs

    def get_modified(self, file):
        """Returns (apparent) file modification time.

        Note:
            Only miilsecond precision is supported as the ultimate target for
            this value is MongoDB, which only supports milliseconds due to a
            deficiency in the BSON specification.
        """
        if getattr(self, 'created') is not None:
            return getattr(self, 'created')
        else:
            stat_cache = getattr(self, '_stat', None)
            if stat_cache is not None:
                t = stat_cache.st_mtime
            else:
                t = os.path.getmtime(file)
            return msec_precision(datetime.datetime.fromtimestamp(t))

    def get_type(self, file):
        """Resolves file type for a given file"""
        return infer_filetype(file).label

    def __checksum_sha256(self, file):
        """Compute sha256 checksum for a file

        Args:
            file(str): Path to file

        Returns:
            str: Current digest as a hexadecial string
        """
        if not os.path.isfile(file):
            return None
        try:
            hash_sha = hashlib.sha256()
            with open(file, "rb") as f:
                for chunk in iter(lambda: f.read(self._block_size), b""):
                    hash_sha.update(chunk)
            return hash_sha.hexdigest()
        except Exception as exc:
            raise OSError('Failed to compute sha256 for {}'.format(file), exc)

    # @classmethod
    def checksum_xxhash(self, file, return_type='int'):
        """Compute xxhash digest for a file

        Args:
            file (str): Path to file
            return_type (str, optional): Type of digest to return [``str``, ``int``]

        Returns:
            int64: Current digest as an integer

        Note:
            See https://cyan4973.github.io/xxHash/ for details on xxHash
        """
        if not os.path.isfile(file):
            return None
        try:
            hash_xxhash = xxhash.xxh64(seed=self.XXHASH64_SEED)
            with open(file, "rb") as f:
                for chunk in iter(lambda: f.read(self._block_size), b""):
                    hash_xxhash.update(chunk)
            if return_type == 'int':
                # Note: xxh64 generates an unsigned 64bit integer, but
                # Mongo can only store int64. We solve this by converting
                # to int64 by subtracting the max size for int64
                digest = hash_xxhash.intdigest() - sys.maxsize
                # print('TYPE.xxHASH', type(digest))
                # print('VAL.xxHash', str(digest))
                return digest
            elif return_type == 'str':
                return hash_xxhash.hexdigest()
        except Exception as exc:
            raise OSError('Failed to compute xxh64 for {}'.format(file), exc)
