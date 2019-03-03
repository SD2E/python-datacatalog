from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object

import os
import sys
import inspect
import json
import copy
import datetime
import base64

from pprint import pprint
from slugify import slugify
from jsondiff import diff

from ... import settings
from ... import config
from ...constants import CatalogStore
from ...dicthelpers import data_merge, flatten_dict, linearize_dict
from ...identifiers.typeduuid import catalog_uuid
from ...jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from ...mongo import db_connection, ReturnDocument, UUID_SUBTYPE, ASCENDING, DuplicateKeyError
from ...tokens import generate_salt, get_token, validate_token, validate_admin_token
from ...utils import time_stamp, current_time, msec_precision
from ... import tenancy

from .heritableschema import DocumentSchema, HeritableDocumentSchema
from .heritableschema import formatChecker, DateTimeEncoder
from .extensible import ExtensibleAttrDict
from .exceptions import *

__all__ = ['LinkedStore', 'StoreInterface', 'DocumentSchema',
           'HeritableDocumentSchema', 'CatalogError', 'CatalogUpdateFailure',
           'CatalogQueryError', 'DuplicateKeyError', 'time_stamp',
           'msec_precision', 'validate_token',
           'DEFAULT_LINK_FIELDS', 'DEFAULT_MANAGED_FIELDS',
           'AgaveError', 'AgaveHelperError', 'validate_admin_token']

DEFAULT_LINK_FIELDS = ('child_of', 'derived_from', 'generated_by')
"""Default set of named linkages between LinkedStore documents"""
DEFAULT_MANAGED_FIELDS = ('uuid', '_admin', '_properties', '_salt', '_enforce_auth')
"""Default set of keys managed by LinkedStore internal logic"""

class LinkedStore(object):
    """JSON-schema informed MongoDB document store with diff-based logging

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        _tenant (str): Description of `attr1`.
        _project (str): Description of `attr1`.
        _owner (str): Description of `attr1`.
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
    UPDATE_POLICIES = ('drop', 'replace', 'merge')
    """Set of policies for updating a LinkedStore document"""
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

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        self._tenant = tenancy.current_tenant()
        """TACC.cloud tenant that owns this document.
        """
        self._project = tenancy.current_project()
        """TACC.cloud project that owns this document
        """
        self._owner = tenancy.current_username()
        """TACC.cloud username that owns this document
        """

        self.session = session
        """Optional correlation string for interlinked events
        """

        self.debug = False
        if isinstance(config.get('debug', None), bool):
            setattr(self, 'debug', config.get('debug'))

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
        """Indexed fields defined in document.json
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
        self.agave_system = CatalogStore.agave_storage_system
        self.base = CatalogStore.agave_root_dir
        self.store = CatalogStore.uploads_dir + '/'
        # Initialize
        # self._post_init()

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

    def setup(self):
        """Set up the MongoDB collection that houses data for the LinkedStore"""
        setattr(self, 'db', db_connection(self._mongodb))
        setattr(self, 'coll', self.db[self.name])
        setattr(self, 'logcoll', self.db['updates'])

        # Index on identifiers must be unique
        UNIQUE_INDEXES = getattr(self, 'identifiers')
        LINKAGE_INDEXES = self.LINK_FIELDS
        OTHER_INDEXES = getattr(self, 'otherindexes')
        ALL_INDEXES = list()
        try:
            # Build indexes for the identifiers, where uniqueness is enforced
            for field in UNIQUE_INDEXES:
                if field not in self.NEVER_INDEX_FIELDS:
                    self.coll.create_index([(field, ASCENDING)], unique=True, sparse=True)
                    ALL_INDEXES.append(field)
            # Create array indexes for linkage fields
            for field in LINKAGE_INDEXES:
                if field not in self.NEVER_INDEX_FIELDS:
                    self.coll.create_index([(field, ASCENDING)])
                    ALL_INDEXES.append(field)
            # Create simple indexes on the non-redundant list of fields from
            # schema.__indexes and schema.required, excluding fields
            # marked as identifiers or uuid-contributing fields
            for field in OTHER_INDEXES:
                if field not in self.NEVER_INDEX_FIELDS:
                    self.coll.create_index([(field, ASCENDING)])
                    ALL_INDEXES.append(field)
            # Contains names of all indexed fields - useful for validation
            setattr(self, '_indexes', list(set(ALL_INDEXES)))
        except Exception as exc:
            # print('Failed to set or enforce indexes.', exc)
            pass

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


    # def update(self, query={}, update={}):
    #     """Update the LinkedStore MongoDB collection

    #     Args:
    #         query (dict): An object describing a MongoDB query
    #         upload (dict): On object encoding a MongoDB update document
    #     """
    #     try:
    #         return self.coll.update(query, update)
    #     except Exception as exc:
    #         raise CatalogError('Update failed', exc)

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
                query = dict()
                try:
                    query[identifier] = kwargs.get(identifier, None)
                except KeyError:
                    pass
                if query[identifier] is not None:
                    # pprint(query)
                    resp = self.coll.find_one(query)
                if resp is not None:
                    break
            return resp
        except Exception as exc:
            raise CatalogError('Query failed', exc)

    def get_typeduuid(self, payload, binary=False):
        if isinstance(payload, dict):
            identifier_string = self.get_linearized_values(payload)
        else:
            identifier_string = str(payload)
        new_uuid = catalog_uuid(identifier_string, uuid_type=self.uuid_type, binary=binary)
        # print('NEW_UUID', new_uuid)
        return new_uuid

    def get_serialized_document(self, document, **kwargs):
        # Serialize values of specific keys to generate a UUID
        union = {**document, **kwargs}
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
        uuid_fields = self.get_uuid_fields()
        ary = list()
        for k in union:
            if k in uuid_fields:
                # print('TYPED_UUID_KEY: {}'.format(k))
                val = union.get(k, 'none')
                try:
                    if isinstance(val, dict):
                        # print('DICT', val)
                        val = json.dumps(val, sort_keys=True, separators=(',', ':'))
                        # print(val)
                    else:
                        val = str(val)
                    ary.append(val)
                except Exception:
                    raise
        ary = sorted(ary)
        linearized = ':'.join(ary)
        # print('TYPED_UUID_LINEARIZED_VAL:', linearized)
        return linearized

    def admin_template(self):
        template = {'owner': self._owner,
                    'project': self._project,
                    'tenant': self._tenant}
        return template

    def __set_properties(self, record, updated=False, source=None):
        """Update the timestamp and revision count for a document

        Args:
            record (dict): A LinkedStore document
            updated (bool): Forces timestamp and revision to increment
            source (str, optional): Source URI for the current update

        Returns:
            dict: Object containing the updated LinkedStore document
        """
        ts = msec_precision(current_time())

        if source is None:
            source = config.Environment.source
        # Amend record with _properties if needed
        if '_properties' not in record:
            record['_properties'] = {'created_date': ts,
                                     'modified_date': ts,
                                     'revision': 0,
                                     'source': source}
        elif updated is True:
            record['_properties']['modified_date'] = ts
            record['_properties']['revision'] = record['_properties']['revision'] + 1
        return record

    def __set_admin(self, record):
        # Stubbed-in support for multitenancy, projects, and ownership
        if '_admin' not in record:
            record['_admin'] = self.admin_template()
        return record

    def __set_salt(self, record):
        # Stubbed-in support for update token
        if '_salt' not in record:
            record['_salt'] = generate_salt()
        return record

    def set_private_keys(self, record, updated=False, source=None):
        record = self.__set_properties(record, updated, source)
        record = self.__set_admin(record)
        record = self.__set_salt(record)
        return record

    def get_diff(self, source={}, target={}, action='update'):
        """Determine the differences between two documents

        Generates a document for the `updates` store that describes the diff
        between source and target documents. The resulting document includes
        the document UUID, a timestamp, the document's tenancy details, and
        the JSON-diff encoded in URL-safe base64. The encoding is necessary
        because JSON diff and patch formats include keys beginning with `$`,
        which are prohibited in MongoDB documents.

        Args:
            source (dict): Source document
            target (dict): Target document
            action (str): Type of update action to represent

        Returns:
            dict: A new json-diff update document
        """

        ts = msec_precision(current_time())
        docs = [copy.deepcopy(source), copy.deepcopy(target)]
        document_uuid = source.get('uuid', target.get('uuid', None))

        if document_uuid is None:
            raise KeyError('Unable to find "uuid" in source or target')

        if '_admin' in source:
            document__admin = source.get('_admin')
        else:
            document__admin = None

        for doc in docs:
            # Filter out specific top-level keys
            for filt in ('uuid', '_id'):
                if filt in doc:
                    del doc[filt]
            # Filter out _private top-level keys
            for key in list(doc.keys()):
                if key.startswith('_'):
                    del doc[key]
            # Filter out linkages
            #
            # Cannot do this at present because it prevents writes
            # as we look at the diff before deciding whether to actually
            # write a database record
            #
            # for filt in self.LINK_FIELDS:
            #     if filt in doc:
            #         del doc[filt]

        safe_docs = list()
        for doc in docs:
            doc1 = json.loads(json.dumps(doc, cls=DateTimeEncoder))
            safe_docs.append(doc1)

        delta = diff(safe_docs[0], safe_docs[1], syntax='explicit', dump=True)

        delta_dict = json.dumps(json.loads(delta), indent=0, separators=(',', ':'))
        # Pack the diff into base64 because mongo can't deal with keys
        # containing $ or . characters. It also compacts
        delta_enc = base64.urlsafe_b64encode(delta_dict.encode('utf-8'))
        diff_doc = {'uuid': document_uuid, 'date': ts, 'diff': delta_enc, 'action': action}
        # Lift over tenant key
        if document__admin is not None:
            diff_doc['_admin'] = document__admin

        return diff_doc

    def add_update_document(self, document_dict, uuid=None, token=None, strategy='merge'):
        """Create or replace a managed document

        Generic class to create or update LinkedStore documents. Handles typed
        UUID generation, manages version and timestamp metadata, implements
        tenant/project/user functions, enforces per-document authorization, and
        implements diff-based update log.

        Args:
            document_dict (dict): Contents of the document to write or replace
            uuid (string, optional): The document's UUID5, which is assigned automatically on creation
            token (str): A short alphanumeric string that authorizes edits to the document
            strategy (str): Specifies the approach for updating contents of the document

        Raises:
            CatalogError: Raised when document cannot be written or updated

        Returns:
            dict: Dict representation of the document that was written

        """
        doc_id = None
        doc_uuid = uuid
        document_dict = dict(document_dict)
        document = copy.deepcopy(document_dict)
        # FIXME: Implement optional validation against self.schema

        uuid_key = self.get_uuid_fields()
        try:
            doc_id = document_dict.get(self.get_uuid_fields()[0])
        except KeyError:
            raise CatalogError('Document lacks primary identifying key "{}"'.format(uuid_key))

        # Validate UUID
        if 'uuid' in document_dict and doc_uuid is not None:
            if doc_uuid != document_dict['uuid']:
                raise CatalogError('document_dict.uuid and uuid parameter cannot be different')

        # Assign a Typed_UUID5 if one is not specified
        if 'uuid' not in document_dict:
            doc_uuid = self.get_typeduuid(document_dict, False)
            document['uuid'] = doc_uuid

        # Attempt to fetch the record using identifiers in schema
        db_record = self.coll.find_one({'uuid': document['uuid']})
        # pprint(db_record)

        # Add or upodate based on result
        if db_record is None:
            return self.add_document(document, token)
        else:
            if strategy == 'replace':
                return self.replace_document(db_record, document, token)
            elif strategy == 'merge':
                return self.update_document(db_record, document, token)
            elif strategy == 'drop':
                # Delete first, then add. This is currently expensive due to 2x
                # database lookup and also not delete linkage references
                self.delete_document(db_record['uuid'], token)
                # Filter private keys and linkages
                for key in list(db_record.keys()):
                    if key.startswith('_'):
                        del db_record[key]
                for linkage in self.LINK_FIELDS:
                    if linkage in db_record:
                        del db_record[linkage]
                # pprint(db_record)
                return self.add_update_document(db_record)
            else:
                raise CatalogError('{} is not a known update strategy'.format(strategy))

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
        db_record = self.set_private_keys(document, updated=False)
        try:
            result = self.coll.insert_one(db_record)
            resp = self.coll.find_one({'_id': result.inserted_id})
            if resp is not None:
                diff_record = self.get_diff(source=dict(), target=db_record, action='create')
                try:
                    self.logcoll.insert_one(diff_record)
                except Exception:
                    # Ignore log failures for now
                    pass
            # Issue and return an update token, even though most of the
            # tooling does not yet use it
            token = get_token(db_record['_salt'], self.get_token_fields(db_record))
            resp['_update_token'] = token
            return resp
        except DuplicateKeyError:
            # print('Unexpectedly found this document in database')
            return self.update_document({'uuid': document['uuid']}, document, token)
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

        # Validate record x token
        # Note: validate_token() always returns True as of 10-19-2018
        # pprint(source_document)
        if self._enforce_auth:
            try:
                validate_token(token, source_document['_salt'], self.get_token_fields(source_document))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)

        # Update
        diff_record = self.get_diff(source=source_document, target=target_document, action='replace')
        # b'e30=' is the base64-encoded version of {}
        if diff_record['diff'] != b'e30=':
            # Transfer _private and identifier fields to document
            for key in list(source_document.keys()):
                if key.startswith('_') or key in ('uuid', '_id'):
                    target_document[key] = source_document[key]
            # Update _properties
            document = self.__set_properties(target_document, updated=True)
            # Lift over linkages
            for key in self.LINK_FIELDS:
                if key in source_document and key in target_document:
                    document[key] = target_document.get(key, list())
            # Update the record
            uprec = self.coll.find_one_and_replace(
                {'uuid': document['uuid']}, document,
                return_document=ReturnDocument.AFTER)
            token = get_token(uprec['_salt'], self.get_token_fields(uprec))
            uprec['_update_token'] = token
            # self.logcoll.insert_one(diff_record)
            try:
                self.logcoll.insert_one(diff_record)
            except Exception:
                # Ignore log failures for now
                pass
            # pprint(uprec)
            return uprec
        else:
            # There was no detectable difference, so return original doc
            token = get_token(source_document['_salt'], self.get_token_fields(source_document))
            source_document['_update_token'] = token
            return source_document

    def update_document(self, source_document, target_document, token=None, merge_dicts='right', merge_lists='append', linkage_policy='extend'):
        """Update a document identified by typed UUID

        Update a document by UUID with additional contents. Update applies a
        merge function on the source and target documents, with behavior for
        generic dict and list values is defined by `merge_dicts` and
        `merge_lists`, respectively. Linkage fields are updated according to
        the policy specified in `linkage_policy`. Managed fields `_admin`,
        `_salt`, and `_properties` are not affected.

        Args:
            source_document (dict): Original contents of the document
            target_document (dict): Revised contents of the document (can be a fragment)
            token (str): Short alphanumeric string authorizing edits to the document
            merge_dicts (str, optional): Directionality for dictionary merge (default: `right`)
            merge_lists (str, optional): Strategy for reconciling lists between source and target (default: `append`)
            linkage_polict (str, optional): Strategy for accepting new linkages from target_document (default: `extend`)

        Raises:
            CatalogError: Raised when document cannot be updated

        Returns:
            dict: Dict representation of the updated document content
        """
        # Validate record x token
        # Note: validate_token() always returns True as of 10-19-2018
        # pprint(source_document)
        if self._enforce_auth:
            try:
                validate_token(token, source_document['_salt'], self.get_token_fields(source_document))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)

        merge_document = copy.deepcopy(source_document)
        # Strip out managed document keys
        for k in list(merge_document.keys()):
            if k.startswith('_'):
                try:
                    del merge_document[k]
                except Exception:
                    pass
                try:
                    del target_document[k]
                except Exception:
                    pass
        # Merge documents
        merged_document = data_merge(merge_document, target_document)
        # Compute diff
        diff_record = self.get_diff(source=merge_document, target=merged_document, action='update')
        if diff_record['diff'] != b'e30=':
            # Transfer _private and identifier fields to document
            for key in list(source_document.keys()):
                if key.startswith('_') or key in ('uuid', '_id'):
                    merged_document[key] = source_document[key]

            # Update _properties for merged_document
            merged_document = self.__set_properties(merged_document, updated=True)
            # Update linkages
            merged_document = self.update_linkages(merged_document, target_document)
            # Update the record
            uprec = self.coll.find_one_and_replace(
                {'uuid': merged_document['uuid']}, merged_document,
                return_document=ReturnDocument.AFTER)
            # print('UPREC', uprec)
            token = get_token(uprec['_salt'], self.get_token_fields(uprec))
            uprec['_update_token'] = token
            # self.logcoll.insert_one(diff_record)
            try:
                self.logcoll.insert_one(diff_record)
            except Exception:
                # Ignore log failures for now
                pass
            # pprint(uprec)
            return uprec
        else:
            # There was no detectable difference, so return original doc
            token = get_token(source_document['_salt'], self.get_token_fields(source_document))
            source_document['_update_token'] = token
            return source_document

    def update_linkages(self, document, target_document, policy='extend', fields=[]):
        """Update the linkages in `document` with values from `target_document`

        This method is applied to a document to update its linkage fields using
        the contents of target_document. The update behavior is determined by
        the value of linkage_opt: `extend` adds any members not present in
        `target_document` to `document`; `replace` replaces the contents of
        `document` with `target_document`. By default all linkage fields are
        processed, but if `fields` is passed (and is a list), then only the
        named linkage fields will be updated.

        Args:
            document (dict): The document whose linkage fields will be modified
            target_document (dict): The document containing new values for linkage fields
            policy (string, optional): The policy for updating linkage fields
            fields (list, optional): List of linkage fields to update. Defaults to all if not passed.

        Raises:
            ValueError: Raised on invalid value for `linkage_opt` or `fields` or
            when values of linkage fields are not lists.

        Returns:
            dict: Dict representation of the updated content for the document

        """
        if policy not in self.LINKAGE_POLICIES:
            raise ValueError('{} is not a valid value for linkage_opt'.format(policy))
        if not isinstance(fields, list):
            raise ValueError('Value for "fields" must be a list')
        if fields == []:
            fields = self.LINK_FIELDS
        elif set(list(fields)).issubset(set(self.LINK_FIELDS)) is False:
            raise ValueError('Invalid value in "fields" list')

        for field in fields:
            doc_val = document.get(field, list())
            target_doc_val = target_document.get(field, list())
            new_val = list()
            if policy == 'extend':
                new_val = doc_val
                new_val.extend(target_doc_val)
                new_val = sorted(list(set(new_val)))
            elif policy == 'replace':
                new_val = target_doc_val
            if len(doc_val) > 0:
                document[field] = new_val

        return document

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
        if key in self.READONLY_FIELDS + tuple(self.identifiers) + tuple(self.uuid_fields):
            raise CatalogError('Key {} cannot be directly updated'.format(key))
        db_record = self.find_one_by_uuid(uuid)
        # Note: validate_token() always returns True as of 10-19-2018
        if self._enforce_auth:
            try:
                validate_token(token, db_record['_salt'], self.get_token_fields(db_record))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)
        updated_record = data_merge(db_record, {key: value})
        diff_record = self.get_diff(source=db_record, target=updated_record, action='update')
        if diff_record['diff'] != b'e30=':
            updated_record = self.__set_properties(updated_record, updated=True)
        uprec = self.coll.find_one_and_replace({'uuid': updated_record['uuid']},
                                               updated_record, return_document=ReturnDocument.AFTER)
        try:
            self.logcoll.insert_one(diff_record)
        except Exception:
            # Ignore log failures for now
            pass
        return uprec

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
        db_record = self.coll.find_one({'uuid': uuid})
        if db_record is None:
            raise CatalogError('No document found with uuid {}'.format(uuid))
        else:
            # Validate record x token
            # Note: validate_token() always returns True as of 10-19-2018
            if self._enforce_auth:
                try:
                    validate_token(token, db_record['_salt'], self.get_token_fields(db_record))
                except ValueError as verr:
                    raise CatalogError('Invalid token', verr)
            # Create log entry
            diff_record = self.get_diff(source=db_record, target=dict(), action='delete')
            deletion_resp = None
            try:
                deletion_resp = self.coll.delete_one({'uuid': uuid})
                try:
                    self.logcoll.insert_one(diff_record)
                except Exception:
                    pass
                return deletion_resp
            except Exception as exc:
                raise CatalogError('Failed to delete document with uuid {}'.format(uuid), exc)

    def add_link(self, uuid, linked_uuid, relation='child_of', token=None):
        """Link a Data Catalog record with one or more Data Catalog records

        Args:
            uuid (str): UUID of the subject record
            linked_uuid (str, list): UUID (or list) of the object record(s)
            relation (str, optional): Name of the relation add
            token (str): String token authorizing edits to the subject record

        Returns:
            dict: Contents of the revised Data Catalog record

        Raises:
            CatalogError: Returned if an invalid relation type or unknown UUID is encountered
        """
        rels = list()
        if isinstance(linked_uuid, str):
            linked_uuid = [linked_uuid]
        try:
            doc = self.find_one_by_uuid(uuid)
            if doc is not None:
                if relation in list(doc.keys()):
                    rels = doc.get(relation)
                    for luuid in linked_uuid:
                        if luuid not in rels:
                            if uuid != luuid:
                                rels.append(luuid)
                    rels = sorted(rels)
                # Create relation if allowed by schema
                elif relation in list(self.document_schema['properties'].keys()):
                    rels = linked_uuid
                else:
                    raise CatalogError('Relationship {} not supported by document {}'.format(relation, uuid))

                # write
                doc[relation] = rels
                return self.add_update_document(doc, uuid=uuid, token=token, strategy='replace')
            else:
                raise CatalogError('No document found with UUID {}'.format(uuid))
        except Exception as exc:
            raise

    def remove_link(self, uuid, linked_uuid, relation='child_of', token=None):
        """Unlink one Data Catalog record from another

        Args:
            uuid (str): UUID of the subject record
            linked_uuid (str): UUID of the object record
            relation (str, optional): Name of the relation to remove
            token (str): String token authorizing edits to the subject record

        Returns:
            dict: Contents of the revised Data Catalog record

        Raises:
            CatalogError: Returned if an invalid relation type or unknown UUID is encountered
        """
        rels = list()
        try:
            doc = self.find_one_by_uuid(uuid)
            # Create empty relation if supported by schema
            # pprint(self.document_schema)
            if doc is not None:
                if relation in list(doc.keys()):
                    rels = doc.get(relation)
                    try:
                        rels.remove(linked_uuid)
                    except ValueError:
                        pass
                elif relation in list(self.document_schema['properties'].keys()):
                    rels = list()
                else:
                    raise CatalogError('Relationship {} not supported by document {}'.format(relation, uuid))

                # write
                doc[relation] = rels
                return self.add_update_document(doc, uuid=uuid, token=token, strategy='replace')
            else:
                raise CatalogError('No document found with UUID {}'.format(uuid))
        except Exception as exc:
            raise

    def get_links(self, uuid, relation='child_of'):
        """Return linkages to this LinkedStore

        Return a list of typed UUIDs representing all connections between this
        LinkedStore and other LinkedStores. This list can be traversed to return
        a list of all LinkedStore objects using `datacatalog.managers.catalog.get()`

        Args:
            uuid (str): The UUID of the LinkedStore document to query
            relation (str, optional): The linkage relationship to return
        Returns:
            list: A list of typed UUIDs that establish relationhips to other LinkedStores
        """
        doc = self.find_one_by_uuid(uuid)
        if doc is not None:
            if relation in list(doc.keys()):
                return doc.get(relation)
            if relation in list(self.document_schema['properties'].keys()):
                # The relationship could exist as per the schema but is not defined
                return list()
            else:
                raise CatalogError(
                    'Relationship "{}" not available in document {}'.format(
                        relation, uuid))

    def debug_mode(self):
        """Returns True if system is running in debug mode"""
        return settings.DEBUG_MODE

class StoreInterface(LinkedStore):
    """Alias for the LinkedStore defined in this module

    This alias is used generically in methods that iterate over all
    known linikedstores.
    """
    pass
