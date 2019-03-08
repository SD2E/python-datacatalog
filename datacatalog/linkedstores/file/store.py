import collections
import inspect
import json
import jsonschema
import os
import sys
from pprint import pprint
from datacatalog import settings

from ...dicthelpers import data_merge
from ...jsonschemas import DateTimeEncoder, formatChecker, DateTimeConverter
from ...jsonschemas import validate as jsonschema_validate
from ...utils import safen_path, normalize, normpath
from ...stores import abspath
from ...filetypes import infer_filetype
from ...identifiers.typeduuid import uuid_to_hashid, catalog_uuid
from ..basestore import LinkedStore
from ..basestore import HeritableDocumentSchema, JSONSchemaCollection
from ..basestore import CatalogUpdateFailure

DEFAULT_LINK_FIELDS = ('child_of', 'derived_from', 'generated_by', 'derived_using')
FILE_ID_PREFIX = settings.FILE_ID_PREFIX
class FileUpdateFailure(CatalogUpdateFailure):
    pass

class FileDocument(HeritableDocumentSchema):
    """Defines experiment-linked metadata for a file"""

    def __init__(self, inheritance=True, **kwargs):
        super(FileDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class FileRecord(collections.UserDict):
    """New document for FileStore with schema enforcement"""

    PARAMS = [
        ('uuid', False, 'uuid', None),
        ('child_of', False, 'child_of', []),
        ('generated_by', False, 'generated_by', []),
        ('derived_using', False, 'derived_using', []),
        ('derived_from', False, 'derived_from', []),
        ('notes', False, 'notes', [])]

    def __init__(self, value, *args, **kwargs):
        # if 'file_id' not in value:
        #     value['file_id'] = 'file.tacc.' + uuid.uuid1().hex
        ovalue = dict(value)

        # Validate incoming document
        value = dict(value)
        self.schema = FileDocument()
        for k in self.schema.filter_keys():
            try:
                del value[k]
            except KeyError:
                pass
        vvalue = json.loads(json.dumps(value, default=DateTimeConverter))
        jsonschema_validate(vvalue, self.schema.to_dict(),
                            format_checker=formatChecker())

        # Ensure the minimum set of other fields is populated
        #
        # We use a bespoke process rather than relying on the schema for now
        # because file record creation cannot tolerate the overhead of
        # materializing a class definition with python_jsonschema_objects
        for param, req, attr, default in self.PARAMS:
            val = kwargs.get(param, ovalue.get(param, default))
            if val is not None:
                kwargs[param] = val

        super().__init__(value, *args, **kwargs)
        self['name'] = safen_path(self['name'],
                                  no_unicode=False,
                                  no_spaces=True,
                                  url_quote=False)

    def set_token(self, value):
        self['_update_token'] = str(value)

class FileStore(LinkedStore):
    """Manage storage and retrieval of FileDocuments"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(FileStore, self).__init__(mongodb, config, session)
        schema = FileDocument(**kwargs)
        super(FileStore, self).update_attrs(schema)
        self.setup()

    def add_update_document(self, document_dict, uuid=None, token=None, strategy='merge'):

        if not isinstance(document_dict, FileRecord):
            document_dict = FileRecord(document_dict)

        # Generate file_id from name if not present
        if 'file_id' not in document_dict:
            document_dict['file_id'] = FILE_ID_PREFIX + uuid_to_hashid(
                catalog_uuid(document_dict['name'], uuid_type='file'))
        resp = super().add_update_document(document_dict,
                                           uuid=uuid, token=token,
                                           strategy=strategy)
        new_resp = FileRecord(resp)
        new_resp.set_token(resp.get('_update_token', None))
        return new_resp

    def index(self, filename, token=None, **kwargs):
        """Capture a skeleton metadata entry for a file

        Args:
            filename (str): Agave-canonical absolute path to the target file

        Returns:
            dict: A LinkedStore document containing file details
        """
        # print('FIXITY.STORE.INDEX ' + filename)
        self.name = normpath(filename)
        self.abs_filename = abspath(self.name)
        file_uuid = self.get_typeduuid(self.name)
        db_record = self.coll.find_one({'uuid': file_uuid})
        file_record = None
        if db_record is None:
            db_record = {'name': filename,
                         'uuid': file_uuid,
                         'type': kwargs.get('type', infer_filetype(
                             filename, check_exists=False).label),
                         'child_of': kwargs.get('child_of', []),
                         'generated_by': kwargs.get('generated_by', [])}
            resp = self.add_update_document(
                db_record, uuid=file_uuid, token=token, strategy='merge')
            file_record = FileRecord(resp)
            file_record.set_token(resp.get('_update_token', token))
        else:
            file_record = FileRecord(db_record)
            file_record.set_token(token)
        return file_record

    def get_typeduuid(self, payload, binary=False):
        identifier_string = None
        if isinstance(payload, dict):
            if 'name' in payload:
                payload['name'] = safen_path(payload['name'])
            identifier_string = self.get_linearized_values(payload)
        else:
            identifier_string = normpath(str(payload))
        # print('IDENTIFIER.string', identifier_string)
        return super().get_typeduuid(identifier_string, binary)

class StoreInterface(FileStore):
    pass
