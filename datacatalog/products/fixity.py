from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import binascii
import datetime
import filetype
import hashlib
import os

from ..catalog import CatalogAttrDict
from ..filetypes import infer_filetype
from ..identifiers.datacatalog_uuid import catalog_uuid
from ..utils import current_time, msec_precision

# FIXME Refactor FileFixityStore to use this

class FileFixityInstance(CatalogAttrDict):
    """Encapsulates the data model and business logic of a fixity record"""
    PARAMS = [('_deleted', False, '_deleted', True),
              ('generated_by', False, 'generated_by', []),
              ('derived_from', False, 'derived_from', []),
              ('child_of', False, 'child_of', [])]
    FILTERS = ['_filename']
    def __init__(self, filename, filepath=None, properties={}, **kwargs):

        self.filename = filename
        if filepath is not None:
            self._filename = filepath
        else:
            self._filename = filename
        self.uuid = catalog_uuid(self.filename)

        self.properties = FixityPropertySet(**properties)
        for param, mandatory, attr, default in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory else kwargs.get(param, default))
            except KeyError:
                raise ValueError(
                    'parameter "{}" is mandatory'.format(param))
            setattr(self, attr, value)

    def sync(self):
        """(Re)load fixity data from disk"""
        COMPARES = ['file_modified', 'size', 'checksum', 'file_type']

        ts = current_time()
        was_modified = False

        initial_vals = {}
        for c in COMPARES:
            try:
                initial_vals[c] = getattr(self.properties, c)
            except AttributeError:
                initial_vals[c] = None

        self.properties.size = self.size()
        self.properties.checksum = self.checksum()
        self.properties.file_type = self.file_type()
        file_modified = self.file_modified()
        if self.properties.file_created is None:
            self.properties.file_created = file_modified
        self.properties.file_modified = file_modified
        if self.properties.created_date is None:
            self.properties.created_date = ts

        for c in COMPARES:
            if getattr(self.properties, c) != initial_vals[c]:
                was_modified = True
                break

        if was_modified:
            self.properties.modified_date = ts
            self.properties.revision = self.properties.revision + 1

        return self

    def add_to_list(self, attname, members):
        if attname in ['child_of', 'derived_from', 'generated_by']:
            orig = getattr(self, attname)
            orig.extend([members])
            new = list(set(orig))
            setattr(self, attname, new)
            return self
        else:
            raise ValueError(attname + ' is not a known list attribute')

    def remove_from_list(self, attname, members):
        if attname in ['child_of', 'derived_from', 'generated_by']:
            orig = getattr(self, attname)
            new = [i for i in orig if i not in [members]]
            setattr(self, attname, new)
            return self
        else:
            raise ValueError(attname + ' is not a known list attribute')

    def size(self):
        """Returns size in bytes for files and 0 for directories"""
        if os.path.isfile(self._filename):
            gs = os.path.getsize(self._filename)
            if gs is None:
                raise OSError(
                    'Unable to get size for {}'.format(self.filename))
            else:
                return gs
        elif os.path.isdir(self._filename):
            return 0

    def checksum(self):
        """Returns checksum for a file"""
        return self.__checksum_sha256()

    def __checksum_sha256(self):
        """Returns sha256 checksum for a file"""
        if not os.path.isfile(self._filename):
            return None
        try:
            hash_sha = hashlib.sha256()
            with open(self._filename, "rb") as f:
                for chunk in iter(lambda: f.read(131072), b""):
                    hash_sha.update(chunk)
            return hash_sha.hexdigest()
        except Exception as exc:
            raise OSError('Unable to compute checksum', exc)

    def file_modified(self):
        """Returns the file's apparent modification time. Note that only
        millisecond precision is supported, which is an inherited deficiency
        from MongoDB and the BSON specification for dates."""
        t = os.path.getmtime(self._filename)
        return msec_precision(datetime.datetime.fromtimestamp(t))

    def file_type(self):
        """Returns the type for a given file"""
        return infer_filetype(self._filename).label

class FixityPropertySet(CatalogAttrDict):
    """Encapsulates a set of fixity properties"""
    PARAMS = [('size', False, 'size', 0),
              ('created_date', False, 'created_date', None),
              ('modified_date', False, 'modified_date', None),
              ('file_created', False, 'file_created', None),
              ('file_modified', False, 'file_modified', None),
              ('file_type', False, 'file_type', None),
              ('revision', False, 'revision', 0),
              ('checksum', False, 'checksum', None),
              ('lab', False, 'lab', None)]
    def __init__(self, **kwargs):
        for param, mandatory, attr, default in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory else kwargs.get(param, default))
            except KeyError:
                raise ValueError(
                    'parameter "{}" is mandatory'.format(param))
            setattr(self, attr, value)
