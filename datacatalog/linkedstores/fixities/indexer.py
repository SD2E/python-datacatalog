import binascii
import datetime
import filetype
import hashlib
import os

# from ..catalog import CatalogAttrDict
from filetypes import infer_filetype
from pathmappings import level_for_filepath
from .schema import FixityDocument, msec_precision

class FixityIndexer(object):
    METHOD_ATTRS = ('type', 'created', 'modified', 'size', 'checksum', 'level')
    CHECKSUM_BLOCKSIZE = 131072
    DEFAULT_SIZE = -1

    def __init__(self, filename, **kwargs):
        self.filename = filename
        # set abspath on filesystem
        self._abspath = filename
        self._updated = False
        for m in self.METHOD_ATTRS:
            value = None
            if m in kwargs:
                value = kwargs[m]
            setattr(self, m, value)

    def sync(self):
        setattr(self, '_updated', False)
        for method_attr in self.METHOD_ATTRS:
            addressable_method = getattr(self, 'get_' + method_attr)
            old_value = getattr(self, method_attr, None)
            new_value = addressable_method(self._abspath)
            if new_value != old_value:
                setattr(self, '_updated', True)
            setattr(self, method_attr, new_value)
        return self

    def updated(self):
        return getattr(self, '_updated', False)

    def get_checksum(self, file, algorithm='sha256'):
        # TODO Implement other methods since this is gonna get slow
        cksum = self.__checksum_sha256(file)
        return cksum

    def get_created(self, file):
        """Returns (apparent) file creation time.

        Note that only msec precision is supported, an inherited deficiency
        from the BSON date specification."""
        if getattr(self, 'created') is not None:
            return getattr(self, 'created')
        else:
            t = os.path.getmtime(file)
            return msec_precision(datetime.datetime.fromtimestamp(t))

    def get_level(self, file):
        """Returns processing level based on prefix of file path"""
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
        """Returns sha256 checksum for a file"""
        if not os.path.isfile(file):
            return None
        try:
            hash_sha = hashlib.sha256()
            with open(file, "rb") as f:
                for chunk in iter(lambda: f.read(self.CHECKSUM_BLOCKSIZE), b""):
                    hash_sha.update(chunk)
            return hash_sha.hexdigest()
        except Exception as exc:
            ('Failed to compute checksum for {}'.format(file))
