import binascii
import datetime
import filetype
import hashlib
import xxhash
import os
import sys
from pprint import pprint

from ...filetypes import infer_filetype
from ...pathmappings import level_for_filepath
from ...pathmappings import normalize, abspath, relativize
from .schema import FixityDocument, msec_precision

class FixityIndexer(object):
    """Captures fixed details for a given file"""
    CHECKSUM_BLOCKSIZE = 131072
    """Chunk size for computing checksum"""
    DEFAULT_SIZE = -1
    """Default size in bytes when it cannot be determined"""
    XXHASH32_SEED = 2573985330
    """Seed for xxHash 32-bit fingerprinting"""
    XXHASH64_SEED = 3759046909696704950
    """Seed for xxHash 64-bit fingerprinting"""

    __PARAMS = [('name', 'name', False, None),
                ('version', 'version', False, 0),
                ('type', 'type', True, None),
                ('created', 'created', True, None),
                ('modified', 'modified', True, None),
                ('size', 'size', True, None),
                ('checksum', 'checksum', True, None),
                ('fingerprint', 'fingerprint', True, None),
                ('level', 'level', False, None),
                ('uuid', 'uuid', False, None),
                ('child_of', 'child_of', False, []),
                ('generated_by', 'generated_by', False, []),
                ('derived_from', 'derived_from', False, [])]

    def __init__(self, abs_filename, schema={}, **kwargs):
        self.name = kwargs.get('name')
        # set._abspath on filesystem
        self._abspath = abspath(self.name)
        self._updated = False

        for key, attr, init, default in self.__PARAMS:
            value = None
            if key in kwargs:
                value = kwargs.get(key, default)
            setattr(self, attr, value)

    def sync(self):
        """Fetch latest values for indexing target"""
        setattr(self, '_updated', False)
        for key, attr, func, default in self.__PARAMS:
            if func:
                addressable_method = getattr(self, 'get_' + attr)
                old_value = getattr(self, attr, None)
                try:
                    new_value = addressable_method(self._abspath)
                    if new_value != old_value:
                        setattr(self, '_updated', True)
                    setattr(self, attr, new_value)
                    # print('ATTR', key, attr, new_value)
                except Exception as exc:
                    pprint(exc)

        # Level is based on the managed path not the absolute storage path
        setattr(self, 'level', self.compute_level(self.name))
        # print('sync.attr:value {}:{}'.format(attr, new_value))
        if self._updated is True:
            setattr(self, 'version', getattr(self, 'version', 0) + 1)
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
        """Helper to manage ``updated`` state"""
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

    def get_fingerprint(self, file, algorithm='xxh64'):
        """Compute fast fingerprint for indexing target

        Args:
            file (str): Absolute path to the file
            algorithm (str, optional): Fingerprint algorithm to use

        Returns:
            str: Hexadecimal checksum for the file
        """
        cksum = FixityIndexer.checksum_xxhash(file)
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
            t = os.path.getmtime(file)
            return msec_precision(datetime.datetime.fromtimestamp(t))

    def compute_level(self, file):
        """Returns processing level for a file

        Args:
            file (str): Absolute path to the file

        Returns:
            str: One of the known data processing levels
        """
        return level_for_filepath(file)

    def get_size(self, file):
        """Returns size in bytes for files (or DEFAULT_SIZE if unknown)"""
        gs = self.DEFAULT_SIZE
        if os.path.isfile(file):
            gs = os.path.getsize(file)
            if gs is None:
                raise OSError(
                    'Failed to get size of {}'.format(file))
        return gs

    def get_type(self, file):
        """Resolves file type for a given file"""
        return infer_filetype(file).label

    def get_modified(self, file):
        """Returns (apparent) file modification time.

        Note that only msec precision is supported, an inherited deficiency
        from the BSON date specification."""
        t = os.path.getmtime(file)
        return msec_precision(datetime.datetime.fromtimestamp(t))

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
                for chunk in iter(lambda: f.read(self.CHECKSUM_BLOCKSIZE), b""):
                    hash_sha.update(chunk)
            return hash_sha.hexdigest()
        except Exception as exc:
            raise OSError('Failed to compute sha256 for {}'.format(file), exc)

    @classmethod
    def checksum_xxhash(cls, file, return_type='int'):
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
            hash_xxhash = xxhash.xxh64(seed=cls.XXHASH64_SEED)
            with open(file, "rb") as f:
                for chunk in iter(lambda: f.read(cls.CHECKSUM_BLOCKSIZE), b""):
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
