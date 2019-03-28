import os
import sys
import inspect
import json
import copy
import datetime
import base64

from pprint import pprint
from slugify import slugify
from pymongo.database import Database
from datacatalog import settings
from datacatalog import linkages
from datacatalog import logger

from ...dicthelpers import data_merge, flatten_dict, linearize_dict
from ...identifiers.typeduuid import catalog_uuid, get_uuidtype
from ...jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from ...mongo import db_connection, ReturnDocument, UUID_SUBTYPE, ASCENDING, DuplicateKeyError
from ...stores import StorageSystem, ManagedStores, PathMappings
from ...tokens import generate_salt, get_token, validate_token, validate_admin_token
from ...utils import time_stamp, current_time, msec_precision
from ... import tenancy

from .diff import get_diff
from .exceptions import (CatalogError, CatalogQueryError,
                         CatalogUpdateFailure, CatalogDataError,
                         CatalogDatabaseError)
from .heritableschema import DocumentSchema, HeritableDocumentSchema
from .heritableschema import formatChecker, DateTimeEncoder
from .linkmanager import LinkageManager
from .merge import json_merge
from .record import Record
from .extensible import ExtensibleAttrDict
from .mongomerge import pre_merge_filter

from . import strategies
from . import managedfields

__all__ = ['LinkedStore', 'StoreInterface', 'DocumentSchema',
           'HeritableDocumentSchema', 'CatalogError', 'CatalogUpdateFailure',
           'CatalogQueryError', 'DuplicateKeyError', 'time_stamp',
           'msec_precision', 'validate_token',
           'DEFAULT_LINK_FIELDS', 'DEFAULT_MANAGED_FIELDS',
           'validate_admin_token', 'linkages']

DEFAULT_LINK_FIELDS = linkages.DEFAULT_LINKS
DEFAULT_MANAGED_FIELDS = managedfields.ALL

class LinkedStore(LinkageManager):
    """JSON-schema informed MongoDB document store with diff-based logging

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        _mongodb (dict): MongoDB connection details
        coll (str): MongoDB collection for documents
        db (:obj:`dict`): Active MongoDB connection
        debug (bool): Description of `attr1`.
        logcoll (str): MongoDB collection for update log
        session (str): Description of `attr1`

        name (str): Human-readable name of the store's JSON schema
        schema (obj:`dict`): A JSON schema document
        schema_name (str): Filename for use by inter-schema references
        identifiers (list): Ordered list of keys that can be used to uniquely retrieve documents in this schema
        uuid_type (str): The specific type of TypedUUID mapped from identifiers
        uuid_fields (list): Ordered list of keys used to compose a typed UUID

    """
    LINK_FIELDS = DEFAULT_LINK_FIELDS
    """Allowed linkage types for this LinkedStore"""
    MANAGED_FIELDS = DEFAULT_MANAGED_FIELDS
    """Fields in this LinkedStore that are managed solely by the framework"""
    READONLY_FIELDS = LINK_FIELDS + MANAGED_FIELDS
    """Additional fields that are read-only in this LinkedStore"""
    PROPERTIES_TEMPLATE = {'_properties': {'created_date': None, 'revision': 0, 'modified_date': None}}
    """Template for a properties subdocument"""
    TOKEN_FIELDS = ('uuid', '_admin')
    """Default set of keys used to issue update tokens"""
    MERGE_DICT_OPTS = ('left', 'right', 'replace')
    """Set of valid strategies for merging dictionaries"""
    MERGE_LIST_OPTS = ('append', 'replace')
    """Set of valid strategies for merging lists"""
    LINKAGE_POLICIES = ('extend', 'replace')
    """Set of valid strategies for updating document linkages"""
    NEVER_INDEX_FIELDS = ('data')
    """Fields that should never be indexed"""
    LOG_JSONDIFF_UPDATES = settings.LOG_UPDATES

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        self.logger = logger.get_logger(__name__)
        self.debug = settings.DEBUG_MODE
        self.session = session
        """Optional correlation string for interlinked events
        """
        self._enforce_auth = False
        """Require valid update token to edit document"""
        # MongoDB setup
        self._mongodb = mongodb
        """Connection object for MongoDB
        """
        self.db = None
        """Name of MongoDB database housing this LinkedStore
        """
        self.coll = None
        """Name of MongoDB collection housing this LinkedStore
        """
        self.logcoll = None
        """Name of MongoDB collection housing the general update log
        """
        # setup based on schema extended properties
        self.schema_name = None
        """Canonical filename for the document's JSON schema
        """
        self.schema = None
        """Dictionary containing the LinkedStore's object schema
        """
        self.document_schema = None
        """Dictionary containing the LinkedStore's full document schema
        """
        self.identifiers = None
        """List of identifying keys for this LinkedStore
        """
        self.otherindexes = None
        """Indexed fields defined in schema.json
        """
        self.name = None
        """Human-readable name of the LinkedStore schema
        """
        self.uuid_type = None
        """Named type for this LinkedStore
        """
        self.uuid_fields = None
        """List of keys that are rolled into the document's UUID
        """

        schema = HeritableDocumentSchema(**kwargs)
        self.update_attrs(schema)

        # FIXME Integration with Agave configurations can be improved
        self.agave_system = settings.STORAGE_SYSTEM
        self.base = StorageSystem(self.agave_system).root_dir
        self.store = ManagedStores.prefixes_for_level('0')[0]
        # Initialize
        # self._post_init()

    def setup(self, update_indexes=False):
        """Set up the MongoDB collection that houses data for the LinkedStore"""
        if isinstance(self._mongodb, Database):
            setattr(self, 'db', self._mongodb)
        else:
            setattr(self, 'db', db_connection(self._mongodb))
        setattr(self, 'coll', self.db[self.name])
        setattr(self, 'logcoll', self.db['updates'])

        # Index on identifiers must be unique
        UNIQUE_INDEXES = getattr(self, 'identifiers')
        LINKAGE_INDEXES = self.LINK_FIELDS
        OTHER_INDEXES = getattr(self, 'otherindexes')
        ALL_INDEXES = list()
        # Optionally, update index definitions.
        try:
            # Build indexes for the identifiers, where uniqueness is enforced
            for field in UNIQUE_INDEXES:
                if field not in self.NEVER_INDEX_FIELDS:
                    if update_indexes:
                        self.coll.create_index([(field, ASCENDING)], unique=True, sparse=True)
                    ALL_INDEXES.append(field)
            # Create array indexes for linkage fields
            for field in LINKAGE_INDEXES:
                if field not in self.NEVER_INDEX_FIELDS:
                    if update_indexes:
                        self.coll.create_index([(field, ASCENDING)])
                    ALL_INDEXES.append(field)
            # Create simple indexes on the non-redundant list of fields from
            # schema.__indexes and schema.required, excluding fields
            # marked as identifiers or uuid-contributing fields
            for field in OTHER_INDEXES:
                if field not in self.NEVER_INDEX_FIELDS:
                    if update_indexes:
                        self.coll.create_index([(field, ASCENDING)])
                    ALL_INDEXES.append(field)

            setattr(self, '_indexes', list(set(ALL_INDEXES)))

        # Contains names of all indexed fields - useful for validation
        except Exception:
            self.logger.warn('Unable to reconfigure indexes')
            pass

    def update_attrs(self, schema):
        """Updates LinkedStore with values in loaded schema

        This is used to allow the schema to be patched or amended at runtime

        Args:
            schema (dict): A JSON schema documented loaded into a dict
        """
        setattr(self, 'name', schema.get_collection())
        setattr(self, 'schema', schema.to_dict())
        setattr(self, 'document_schema', schema.to_dict(document=True))
        setattr(self, 'schema_name', schema.get_filename())
        setattr(self, 'identifiers', schema.get_identifiers())
        setattr(self, 'required', schema.get_required())
        setattr(self, 'uuid_fields', schema.get_uuid_fields())
        setattr(self, 'uuid_type', schema.get_uuid_type())

        otherindexes = schema.get_indexes()
        otherindexes.extend(getattr(self, 'identifiers'))
        otherindexes.extend(getattr(self, 'required'))
        otherindexes = sorted(list(
            set(otherindexes) - set(getattr(self, 'identifiers'))))
        # sys.exit(0)
        setattr(self, 'otherindexes', otherindexes)
        return self

    def get_identifiers(self):
        """Returns names of keys whose values will be distinct"""
        return getattr(self, 'identifiers')

    def get_indexes(self):
        """Returns names of all fields indexed in this store"""
        return getattr(self, '_indexes')

    def get_required(self):
        """Returns names of keys required by this document class"""
        return getattr(self, 'required')

    def get_uuid_type(self):
        """Returns UUID type for docuemnts managed by this LinkedStore"""
        return getattr(self, 'uuid_type')

    def get_uuid_fields(self):
        """Returns keys used by this LinkedStore to issue a typed UUID"""
        return getattr(self, 'uuid_fields')

    def get_token_fields(self, record_dict):
        """Get values for issuing a document's update token

        The fields used to define an update token are set in TOKEN_FIELDS. This
        method fetches values from those fields and returns as a list.

        Args:
            record_dict (dict): Contents of the document from which to extract values

        Returns:
            list: List of values from keys matching `TOKEN_FIELDS`

        """
        token_fields = list()
        for key in self.TOKEN_FIELDS:
            if key in record_dict:
                token_fields.append(record_dict.get(key))
        return token_fields

    def query(self, query={}, projection=None,
              attr_dict=False, attr_filters={'private_prefix': '_', 'filters': []}):
        """Query the LinkedStore MongoDB collection and return a Cursor

        Args:
            query (dict): An object describing a MongoDB query
            projection (dict): An object describing a MongoDB projection
            filters (dict): {private_prefix': '_', filters: []}
        """
        query_kwargs = dict()
        try:
            if not isinstance(query, dict):
                query = json.loads(query)
        except Exception as exc:
            raise CatalogError('Query was not resolvable as dict', exc)

        if projection is not None:
            if isinstance(projection, dict):
                proj = projection
            elif isinstance(projection, str):
                proj = json.loads(projection)
            else:
                raise CatalogError('Projection was passed but not resolvable into a dictionary')
            # All went well - add a projection keyword argument
            query_kwargs['projection'] = proj

        try:
            result = self.coll.find(query, **query_kwargs)
            if attr_dict is False:
                return result
            else:
                filtered_result = list()
                for r in result:
                    filtered_result.append(
                        ExtensibleAttrDict(r).as_dict(**attr_filters))
                return filtered_result
        except Exception as exc:
            raise CatalogError('Query failed', exc)

    def find_one_by_uuid(self, uuid):
        """Find and return a LinkedStore document by its typed UUID

        Args:
            uuid (str): The UUID to search for

        Raises:
            CatalogError: Raised when query fails due to an error or invalid value

        Returns:
            dict: Object containing the LinkedStore document
        """
        try:
            self.logger.debug('find_one_by_uuid: {}'.format(uuid))
            query = {'uuid': uuid}
            return self.coll.find_one(query)
        except Exception as exc:
            raise CatalogError('Query failed for uuid'.format(uuid), exc)

    def find_one_by_id(self, **kwargs):
        """Find and return a LinkedStore document by any of its identifiers

        Examples:
            `resp = find_one_by_id(name='uniquename')`
            `resp = find_one_by_id(uuid='105bf45a-6282-5e8c-8651-6a0ff78a3741')`
            `resp = find_one_by_id(id='lab.sample.12345')`

        Raises:
            CatalogError: Raised when query fails due to an error or invalid value

        Returns:
            dict: Object containing the LinkedStore document
        """
        try:
            resp = None
            for identifier in self.get_identifiers():
                self.logger.debug('find_one_by_id: {}'.format(identifier))
                query = dict()
                try:
                    query[identifier] = kwargs.get(identifier, None)
                except KeyError:
                    pass
                if query[identifier] is not None:
                    resp = self.coll.find_one(query)
                if resp is not None:
                    break
            return resp
        except Exception as exc:
            raise CatalogError('Query failed', exc)

    def get_typeduuid(self, payload, binary=False):
        if isinstance(payload, dict):
            self.logger.debug('get_typeduuid received dict')
            identifier_string = self.get_linearized_values(payload)
        else:
            self.logger.debug('get_typeduuid received {}'.format(type(payload)))
            identifier_string = str(payload)
        new_uuid = catalog_uuid(identifier_string, uuid_type=self.uuid_type, binary=binary)
        self.logger.debug('identifier_string: {}'.format(identifier_string))
        self.logger.debug('get_typeduuid => {}'.format(new_uuid))
        return new_uuid

    def get_serialized_document(self, document, **kwargs):
        # Serialize values of specific keys to generate a UUID
        union = {**document, **kwargs}
        self.logger.debug('serializing {}'.format(union))
        uuid_fields = self.get_uuid_fields()
        serialized = dict()
        for k in union:
            if k in uuid_fields:
                # print('TYPED_UUID_KEY: {}'.format(k))
                serialized[k] = union.get(k)
        serialized_document = json.dumps(serialized, indent=0, sort_keys=True, separators=(',', ':'))
        # print('TYPED_UUID_SERIALIZED_VAL:', serialized_document)
        return serialized_document

    def get_linearized_values(self, document, **kwargs):
        # Serialize values of specific keys to generate a UUID
        union = {**document, **kwargs}
        self.logger.debug('linearizing {}'.format(union))
        uuid_fields = self.get_uuid_fields()
        ary = list()
        for k in union:
            if k in uuid_fields:
                # print('TYPED_UUID_KEY: {}'.format(k))
                val = union.get(k, 'none')
                try:
                    if isinstance(val, dict):
                        val = json.dumps(val, sort_keys=True, separators=(',', ':'))
                    else:
                        val = str(val)
                    ary.append(val)
                except Exception:
                    self.exception('Failed to linearize values')
                    raise
        ary.sort()
        linearized = ':'.join(ary)
        self.logger.debug('get_linearized_values: {}'.format(linearized))
        return linearized

    def admin_template(self):
        template = {'owner': tenancy.current_tenant(),
                    'project': tenancy.current_project(),
                    'tenant': tenancy.current_username()}
        return template

    def __set_properties(self, record, updated=False, source=None):
        """Update the timestamp and revision count for a document

        Args:
            record (dict): A LinkedStore document
            updated (bool): Forces timestamp and revision to increment
            source (str, optional): Source of the current update

        Returns:
            dict: Object containing the updated LinkedStore document
        """
        self.logger.debug('updating record properties')
        ts = msec_precision(current_time())
        if source is None:
            source = settings.RECORDS_SOURCE
        # Amend record with _properties if needed
        if '_properties' not in record:
            record['_properties'] = {'created_date': ts,
                                     'modified_date': ts,
                                     'revision': 0,
                                     'source': source}
        elif updated is True:
            self.logger.debug('record is updated: bumping revision and modified_dat')
            record['_properties']['modified_date'] = ts
            record['_properties']['revision'] = record['_properties']['revision'] + 1
        return record

    def __set_admin(self, record):
        # Stubbed-in support for multitenancy, projects, and ownership
        self.logger.debug('updating record admin fields')
        if '_admin' not in record:
            record['_admin'] = self.admin_template()
        return record

    def __set_salt(self, record, refresh=False):
        self.logger.debug('setting record token salt')
        if '_salt' not in record or refresh is True:
            record['_salt'] = generate_salt()
            if refresh:
                self.logger.debug('refreshing record token salt')
        return record

    def set_private_keys(self, record, updated=False, source=None):
        record = self.__set_properties(record, updated, source)
        record = self.__set_admin(record)
        record = self.__set_salt(record)
        return record

    def add_update_document(self, doc_dict, uuid=None, token=None, strategy=strategies.MERGE):

        self.logger.info('add_update_document()')
        self.logger.debug('type(doc_dict) is {}'.format(type(doc_dict)))
        self.logger.debug('value for uuid is {}'.format(uuid))

        # Validate value and appropriateness of uuid if passed
        if uuid is not None:
            # Validate that the UUID resolves to a known type
            self.get_uuid_type() == get_uuidtype(uuid)

        # Validate that all identifiers are present
        for k in self.get_uuid_fields():
            if k not in doc_dict:
                raise KeyError(
                    "Document lacks identifier '{}'".format(k))

        # Compute and inject TypedUUID if needed
        if 'uuid' not in doc_dict:
            new_uuid = self.get_typeduuid(doc_dict, False)
            doc_dict['uuid'] = new_uuid
            self.logger.debug(
                'computed UUID {} for doc_dict'.format(
                    new_uuid))

        # Ensure computed and passed uuid do not conflict
        if uuid is not None:
            if uuid != doc_dict['uuid']:
                raise ValueError("'uuid' {} != document.uuid {}".format(
                    uuid, doc_dict['uuid']))

        # Transform dict into Record, which validates and adds in linkage fields
        # doc_record = Record(doc_dict)
        doc_record = doc_dict
        self.logger.debug('doc_record: {}'.format(doc_dict))
        # Fetch record if exists
        self.logger.debug('trying to retrieve existing document')
        db_record = self.coll.find_one({'uuid': doc_dict['uuid']})

        if db_record is None:
            self.logger.debug('no existing document found')
            return self.add_document(doc_record)
        else:
            if strategy == strategies.REPLACE:
                return self.replace_document(db_record, doc_record, token=token)
            elif strategy == strategies.MERGE:
                return self.update_document(db_record, doc_record, token=token)
            elif strategy == strategies.DROP:
                raise ValueError("'{}' not a supported document policy".format(strategy))

    def add_document(self, document, token=None):
        """Write a new managed document

        Args:
            document (dict): The contents of the document

        Raises:
            CatalogError: Raised when document cannot be written

        Returns:
            dict: Dictionary representation of the new document

        """
        # Decorate the document with our _private keys
        self.logger.info('add_document()')
        db_record = self.set_private_keys(document, updated=False)
        # populate linkages if not existent
        for lf in self.LINK_FIELDS:
            if lf not in db_record:
                db_record[lf] = list()

        try:
            result = self.coll.insert_one(db_record)
            added_doc = self.coll.find_one({'_id': result.inserted_id})
            if added_doc is not None:
                if self.LOG_JSONDIFF_UPDATES:
                    diff_record = get_diff(
                        source=dict(), target=db_record, action='create')
                    self.logger.debug('diff: {}'.format(diff_record))
                    try:
                        self.logcoll.insert_one(diff_record.document())
                    except Exception:
                        self.logger.exception('failed to log document creation')
            else:
                raise CatalogError('response for mongo.insert_one() was None')
            # Issue and return an update token
            token = get_token(db_record['_salt'],
                              self.get_token_fields(db_record))
            added_doc['_update_token'] = token

            self.logger.info('add_document() complete')
            return added_doc

        except DuplicateKeyError:
            # This is only possible if add_document is called directly
            self.logger.warning('add_document() references an existing document: redirecting to update_document()')
            return self.update_document(
                {'uuid': document['uuid']}, document, token=token)

        except Exception as exc:
            raise CatalogError('Failed to create document', exc)

    def replace_document(self, source_document, target_document, token=None):
        """Replace a document distinguished by UUID with a new instance

        Args:
            source_document (dict): The original document
            target_document (dict): The document to replace source with
            uuid (str, optional): The document's UUID5, which is assigned automatically on
            creation
            token (str): A short alphanumeric string that authorizes edits to the document

        Raises:
            CatalogError: Raised when document cannot be replaced

        Returns:
            dict: Dict representation of the new content for the document

        """

        self.logger.info('replace_document()')

        # Validate record x token
        if self._enforce_auth:
            try:
                validate_token(token, source_document['_salt'], self.get_token_fields(source_document))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)

        replaced_doc = source_document
        diff_record = None
        was_updated = True

        if self.LOG_JSONDIFF_UPDATES:
            self.logger.debug('calculating diff for replace')
            diff_record = get_diff(source=source_document,
                                   target=target_document,
                                   action='replace')
            was_updated = diff_record.updated
        else:
            self.logger.debug('skip calculating diff for replace')

        if was_updated:
            self.logger.debug('proceeding with replace()')
            # self.logger.debug('diff: {}'.format(diff_record))
            # Transfer _private and identifier fields to document
            for key in list(source_document.keys()):
                if key.startswith('_') or key in ('uuid', '_id'):
                    target_document[key] = source_document[key]
            # Update _properties
            document = self.__set_properties(target_document, updated=True)
            # Update the salt value, changing the update token
            document = self.__set_salt(document, refresh=True)
            # populate linkages if not existent
            for lf in self.LINK_FIELDS:
                if lf not in document:
                    document[lf] = list()
            # Update the record
            replaced_doc = self.coll.find_one_and_replace(
                {'uuid': document['uuid']}, document,
                return_document=ReturnDocument.AFTER)

            # self.logcoll.insert_one(diff_record)
            if self.LOG_JSONDIFF_UPDATES:
                self.logger.debug('logging replace()')
                try:
                    self.logcoll.insert_one(diff_record.document())
                except Exception:
                    self.logger.exception('failed to log document replace()')
            else:
                self.logger.debug('skip logging replace()')
        else:
            self.logger.debug('skipping replace()')

        token = get_token(replaced_doc['_salt'],
                          self.get_token_fields(replaced_doc))
        replaced_doc['_update_token'] = token

        self.logger.info('replace_document() complete')
        return replaced_doc

    def update_document(self, source_document, target_document, token=None,
                        merge_dicts='right', merge_lists='append',
                        linkage_policy='extend'):

        self.logger.info('update_document()')

        # Validate record x token
        if self._enforce_auth:
            try:
                validate_token(token, source_document['_salt'],
                               self.get_token_fields(source_document))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)

        updated_doc = source_document
        diff_record = None
        was_updated = False

        self.logger.debug('comparing linkages fields')
        diff_linkages = linkages.merge_linkages(source_document,
                                                target_document,
                                                link_fields=self.LINK_FIELDS)
        merge_source = copy.copy(source_document)
        # Strip managed document keys
        self.logger.debug('merging source and target documents')
        merge_source, source_managed_fields = pre_merge_filter(merge_source)
        target_document, target_managed_fields = pre_merge_filter(target_document)
        merged_dest = json_merge(merge_source, target_document)
        was_updated = True

        if self.LOG_JSONDIFF_UPDATES:
            self.logger.debug('calculating diff for update')
            try:
                diff_record = get_diff(source=merge_source,
                                       target=merged_dest,
                                       action='update')
                was_updated = diff_record.updated
            except RuntimeError:
                diff_record = None
                was_updated = True
        else:
            self.logger.debug('skip calculating diff for update')

        if was_updated or diff_linkages.updated:

            self.logger.debug('proceeding with update()')

            # Graft on contents of diff_linkages
            for link_field, link_value in diff_linkages['values'].items():
                merged_dest[link_field] = link_value

            # Lift over private keys
            for key in managedfields.ALL:
                if key in source_managed_fields:
                    merged_dest[key] = source_managed_fields[key]
            # Get original _id field
            try:
                merged_dest['_id'] = source_document['_id']
            except KeyError:
                pass

            # Update _properties for merged_document
            merged_dest = self.__set_properties(merged_dest, updated=True)
            # Cycle the record's _salt to change the token
            merged_dest = self.__set_salt(merged_dest, refresh=True)

            # Update the record
            self.logger.debug('writing to database')
            updated_doc = self.coll.find_one_and_replace(
                {'uuid': merged_dest['uuid']}, merged_dest,
                return_document=ReturnDocument.AFTER)

            # Only log if the document changed
            if self.LOG_JSONDIFF_UPDATES and was_updated:
                self.logger.debug('logging update()')
                try:
                    self.logcoll.insert_one(diff_record.document())
                except Exception:
                    self.logger.exception('failed to log update{}')
            else:
                self.logger.debug('skip logging update()')

        else:
            self.logger.debug('no update required')

        self.logger.debug('generating access token')
        updated_doc['_update_token'] = get_token(updated_doc['_salt'],
                                                 self.get_token_fields(
                                                     updated_doc))

        self.logger.info('update_document() complete')
        return updated_doc

    def write_key(self, uuid, key, value, token=None):
        """Write a value to a top-level key in a document

        Managed interface for writing to specific top-level keys, where some
        keys, namely any that are specified in the schema as identifiers or
        contributors to UUID generation, are enforced to be read-only.

        Args:
            uuid (str): UUID of the target document
            key (str): Name of the document key to write to
            value: Value to write to the designated key
            token (str): Short alphanumeric string authorizing edits to the document

        Raises:
            CatalogError: Raised when a read-only key is specified or an invalid token is passed

        Returns:
            dict: Dict representation of the updated document
        """
        db_record = self.find_one_by_uuid(uuid)

        if self._enforce_auth:
            try:
                validate_token(token, db_record['_salt'],
                               self.get_token_fields(db_record))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)

        if key in self.READONLY_FIELDS + tuple(self.identifiers) + tuple(self.uuid_fields):
            raise CatalogError('Key {} cannot be directly updated'.format(key))


        updated_record = data_merge(db_record, {key: value})
        diff_record = get_diff(source=db_record,
                               target=updated_record,
                               action='update')

        if diff_record.updated:

            self.logger.debug('documents were different - proceeding with update()')
            self.logger.debug('diff: {}'.format(diff_record))

            updated_record = self.__set_properties(updated_record, updated=True)
            self.logger.debug('cycling access token salt')
            updated_record = self.__set_salt(updated_record, refresh=True)

            self.logger.debug('writing to database')
            writekey_doc = self.coll.find_one_and_replace(
                {'uuid': updated_record['uuid']}, updated_record,
                return_document=ReturnDocument.AFTER)

            self.logger.debug('generating access token')
            writekey_doc['_update_token'] = get_token(
                writekey_doc['_salt'],
                self.get_token_fields(writekey_doc))

            self.logger.debug('logging')
            try:
                self.logcoll.insert_one(diff_record.document())
            except Exception:
                self.logger.exception('failed to log document.key update')

            return writekey_doc
        else:
            db_record['_update_token'] = get_token(
                db_record['_salt'],
                self.get_token_fields(db_record))
            return db_record

    def delete_document(self, uuid, token=None):
        """Delete a document by UUID

        Managed interface for removing a document from its linkedstore
        collection by its typed UUID.

        Args:
            uuid (str): UUID of the target document
            token (str): Short alphanumeric string authorizing edits to the document

        Raises:
            CatalogError: Raised when unknown UUID, invalid token is passed, or on general write failure.

        Returns:
            dict: MongoDB deletion response
        """

        self.logger.info('delete_document()')
        # Raises if non-existent
        db_record = self.coll.find_one({'uuid': uuid})

        if self._enforce_auth:
            try:
                validate_token(token, db_record['_salt'],
                               self.get_token_fields(db_record))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)

        diff_record = None
        deletion_resp = None

        if self.LOG_JSONDIFF_UPDATES:
            self.logger.debug('calculating diff for delete')
            diff_record = get_diff(source=db_record, target=dict(), action='delete')
        else:
            self.logger.debug('skip calculating diff for delete')

        # Create log entry
        try:
            self.logger.debug('proceeding with delete()')
            deletion_resp = self.coll.delete_one({'uuid': uuid})
            self.logger.debug('response: {}'.format(deletion_resp))
            if self.LOG_JSONDIFF_UPDATES:
                self.logger.debug('logging delete()')
                try:
                    self.logcoll.insert_one(diff_record)
                except Exception:
                    self.logger.exception('failed to log document delete')
            else:
                self.logger.debug('skip logging delete()')
        except Exception as exc:
            raise CatalogError('Failed to delete document with uuid {}'.format(uuid), exc)

        self.logger.info('delete_document() complete')
        return deletion_resp

    def debug_mode(self):
        """Returns True if system is running in debug mode"""
        return settings.DEBUG_MODE

class StoreInterface(LinkedStore):
    """Alias for the LinkedStore defined in this module

    This alias is used generically in methods that iterate over all
    known linikedstores.
    """
    pass
