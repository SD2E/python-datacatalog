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

from constants import CatalogStore
from utils import time_stamp, current_time, msec_precision
from dicthelpers import data_merge, flatten_dict, linearize_dict
from debug_mode import debug_mode

from jsonschemas import JSONSchemaBaseObject
from tokens import generate_salt, get_token, validate_token
from identifiers.typed_uuid import catalog_uuid

from mongo import db_connection, ReturnDocument, UUID_SUBTYPE, ASCENDING, DuplicateKeyError

from .exceptions import CatalogError, CatalogUpdateFailure, CatalogQueryError
from .documentschema import DocumentSchema
from .heritableschema import HeritableDocumentSchema

__all__ = ['BaseStore', 'StoreInterface', 'DocumentSchema', 'HeritableDocumentSchema', 'CatalogError', 'CatalogUpdateFailure', 'CatalogQueryError', 'DuplicateKeyError', 'time_stamp', 'msec_precision', 'validate_token', 'debug_mode']

class BaseStore(object):
    """Storage interface for JSON schema-informed documents"""
    PROPERTIES_TEMPLATE = {'_properties': {'created_date': None, 'revision': 0, 'modified_date': None}}
    TOKEN_FIELDS = ('uuid', '_admin')
    LINK_FIELDS = ('child_of', 'derived_from', 'generated_by')
    MANAGED_FIELDS = ('uuid', '_admin', '_properties', '_salt')
    READONLY_FIELDS = MANAGED_FIELDS + LINK_FIELDS

    def __init__(self, mongodb, config={}, session=None, **kwargs):

        self._tenant = 'sd2e'
        self._project = 'SD2E-Community'
        self._owner = 'sd2eadm'

        if isinstance(config.get('debug', None), bool):
            self.debug = config.get('debug')
        else:
            self.debug = False

        # This is a correlation string, akin to Reactor.nickname
        self.session = session

        self._mongodb = mongodb
        self.db = None
        self.coll = None
        self.logcoll = None

        # setup based on schema extended properties
        schema = DocumentSchema(**kwargs)
        self.schema = schema.to_dict()
        self.identifiers = schema.get_identifiers()
        self.name = schema.get_collection()
        self.uuid_type = schema.get_uuid_type()
        self.uuid_fields = schema.get_uuid_fields()

        # FIXME Integration with Agave configurations can be improved
        self.agave_system = CatalogStore.agave_storage_system
        self.base = CatalogStore.agave_root_dir
        self.store = CatalogStore.uploads_dir + '/'
        # Initialize
        # self._post_init()

    def get_identifiers(self):
        return getattr(self, 'identifiers')

    def get_uuid_type(self):
        return getattr(self, 'uuid_type')

    def get_uuid_fields(self):
        return getattr(self, 'uuid_fields')

    def setup(self):
        # Database connection and init
        setattr(self, 'db', db_connection(self._mongodb))
        setattr(self, 'coll', self.db[self.name])
        setattr(self, 'logcoll', self.db['updates'])
        if self.coll is not None:
            try:
                self.coll.create_index([('uuid', ASCENDING)], unique=True)
                self.coll.create_index([('child_of', ASCENDING)])
            except Exception as exc:
                raise CatalogError(
                    'Failed to set index on {}.uuid'.format(self.name), exc)

    def query(self, query={}):
        try:
            if not isinstance(query, dict):
                query = json.loads(query)
        except Exception as exc:
            raise CatalogError('Query was not resolvable as dict', exc)
        try:
            return self.coll.find(query)
        except Exception as exc:
            raise CatalogError('Query failed', exc)

    def find_one_by_id(self, **kwargs):
        try:
            resp = None
            for identifier in self.get_identifiers():
                query = dict()
                try:
                    query[identifier] = kwargs.get(identifier, None)
                except KeyError:
                    pass
                if query[identifier] is not None:
                    pprint(query)
                    resp = self.coll.find_one(query)
                if resp is not None:
                    break
            return resp
        except Exception as exc:
            raise CatalogError('Query failed', exc)

    def find_one_by_uuid(self, uuid):
        try:
            query = {'uuid': uuid}
            return self.coll.find(query)[0]
        except Exception as exc:
            raise CatalogError('Query failed for uuid'.format(uuid), exc)

    def set__properties(self, record, updated=False):
        ts = msec_precision(current_time())
        # Amend record with _properties if needed
        if '_properties' not in record:
            record['_properties'] = {'created_date': ts,
                                     'modified_date': ts,
                                     'revision': 0}
        elif updated is True:
            record['_properties']['modified_date'] = ts
            record['_properties']['revision'] = record['_properties']['revision'] + 1
        return record

    def set__admin(self, record):
        # Stubbed-in support for multitenancy, projects, and ownership
        if '_admin' not in record:
            record['_admin'] = {'owner': self._owner,
                                'project': self._project,
                                'tenant': self._tenant}
        return record

    def set__salt(self, record):
        # Stubbed-in support for update token
        if '_salt' not in record:
            record['_salt'] = generate_salt()
        return record

    def set__private_keys(self, record, updated=False):
        record = self.set__properties(record, updated)
        record = self.set__admin(record)
        record = self.set__salt(record)
        return record

    def get_typed_uuid(self, payload, binary=False):
        print('TYPED_UUID_PAYLOAD: {}'.format(payload))
        if isinstance(payload, dict):
            identifier_string = self.get_linearized_values(payload)
        else:
            identifier_string = str(payload)
        new_uuid = catalog_uuid(identifier_string, uuid_type=self.uuid_type, binary=binary)
        print('TYPED_UUID: {}'.format(new_uuid))
        return new_uuid

    def get_serialized_document(self, document, **kwargs):
        # Serialize values of specific keys to generate a UUID
        union = {**document, **kwargs}
        uuid_fields = self.get_uuid_fields()
        serialized = dict()
        for k in union:
            if k in uuid_fields:
                print('TYPED_UUID_KEY: {}'.format(k))
                serialized[k] = union.get(k)
        serialized_document = json.dumps(serialized, indent=0, sort_keys=True, separators=(',', ':'))
        return serialized_document

    def get_linearized_values(self, document, **kwargs):
        # Serialize values of specific keys to generate a UUID
        union = {**document, **kwargs}
        uuid_fields = self.get_uuid_fields()
        ary = list()
        for k in union:
            if k in uuid_fields:
                print('TYPED_UUID_KEY: {}'.format(k))
                val = union.get(k, 'none')
                try:
                    if isinstance(val, dict):
                        val = linearize_dict(val)
                    else:
                        val = str(val)
                    ary.append(val)
                except Exception:
                    pass
        ary = sorted(ary)
        linearized = ':'.join(ary)
        print('TYPED_UUID_LINEARIZED_VAL:', linearized)
        return linearized

    def get_diff(self, source={}, target={}, action='update'):
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

        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime.datetime):
                    return o.isoformat()

                return json.JSONEncoder.default(self, o)

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

    def get_token_fields(self, record_dict):
        token_fields = list()
        for key in self.TOKEN_FIELDS:
            if key in record_dict:
                token_fields.append(record_dict.get(key))
        return token_fields

    def add_update_document(self, document_dict, uuid=None, token=None):
        doc_id = None
        doc_uuid = uuid
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
            doc_uuid = self.get_typed_uuid(document_dict, False)
            document['uuid'] = doc_uuid

        # Attempt to fetch the record using identifiers in schema
        db_record = self.coll.find_one({'uuid': document['uuid']})
        pprint(db_record)

        # Add or upodate based on result
        if db_record is None:

            # Decorate the document with our _private keys
            db_record = self.set__private_keys(document, updated=False)
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
            except Exception as exc:
                raise CatalogError('Failed to write document', exc)
            pprint(db_record)
            sys.exit(1)
        else:

            # Validate record x token
            # Note: validate_token() always returns True as of 10-19-2018
            try:
                validate_token(token, db_record['_salt'], self.get_token_fields(db_record))
            except ValueError as verr:
                raise CatalogError('Invalid token', verr)

            # Update
            diff_record = self.get_diff(source=db_record, target=document, action='update')
            # b'e30=' is the base64-encoded version of {}
            if diff_record['diff'] != b'e30=':
                # Transfer _private and identifier fields to document
                for key in list(db_record.keys()):
                    if key.startswith('_') or key in ('uuid', '_id'):
                        document[key] = db_record[key]
                # Update _properties
                document = self.set__properties(document, updated=True)
                # Update the record
                uprec = self.coll.find_one_and_replace(
                    {'uuid': document['uuid']}, document,
                    return_document=ReturnDocument.AFTER)
                # self.logcoll.insert_one(diff_record)
                try:
                    self.logcoll.insert_one(diff_record)
                except Exception:
                    # Ignore log failures for now
                    pass
                return uprec
            else:
                return db_record

    def write_key(self, uuid, key, value, token=None):
        if key in self.READONLY_FIELDS + tuple(self.identifiers) + tuple(self.uuid_fields):
            raise CatalogError('Key {} cannot be directly updated'.format(key))
        db_record = self.find_one_by_uuid(uuid)
        # Note: validate_token() always returns True as of 10-19-2018
        try:
            validate_token(token, db_record['_salt'], self.get_token_fields(db_record))
        except ValueError as verr:
            raise CatalogError('Invalid token', verr)
        updated_record = data_merge(db_record, {key: value})
        diff_record = self.get_diff(source=db_record, target=updated_record, action='update')
        if diff_record['diff'] != b'e30=':
            updated_record = self.set__properties(updated_record, updated=True)
        uprec = self.coll.find_one_and_replace({'uuid': updated_record['uuid']},
                                               updated_record, return_document=ReturnDocument.AFTER)
        try:
            self.logcoll.insert_one(diff_record)
        except Exception:
            # Ignore log failures for now
            pass
        return uprec

    def delete_document(self, uuid, token=None):
        db_record = self.coll.find_one({'uuid': uuid})
        if db_record is None:
            raise CatalogError('No document found with uuid {}'.format(uuid))
        else:
            # Validate record x token
            # Note: validate_token() always returns True as of 10-19-2018
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
        """Add a new linkage to another document"""
        rels = list()
        try:
            doc = self.query({'uuid': uuid})
            if doc is not None:
                if relation in list(doc.keys()):
                    rels = doc.get(relation)
                    if linked_uuid not in rels:
                        rels.append(linked_uuid)
                        rels = sorted(rels)
                # Create relation if allowed by schema
                elif relation in list(self.schema['properties'].keys()):
                    rels = [linked_uuid]
                else:
                    raise CatalogError('Relationship {} not supported by document {}'.format(relation, uuid))

                # write
                doc[relation] = rels
                resp = self.add_update_document(doc, uuid=uuid, token=token)
                return resp
            else:
                raise CatalogError('No document found with UUID {}'.format(uuid))
        except Exception as exc:
            raise

    def remove_link(self, uuid, linked_uuid, relation='child_of', token=None):
        """Remove a linkage with another document"""
        rels = list()
        try:
            doc = self.query({'uuid': uuid})
            if doc is not None:
                if relation in list(doc.keys()):
                    rels = doc.get(relation)
                    try:
                        rels.remove(linked_uuid)
                    except ValueError:
                        pass
                # Create empty relation if supported by schema
                elif relation in list(self.schema['properties'].keys()):
                    rels = list()
                else:
                    raise CatalogError('Relationship {} not supported by document {}'.format(relation, uuid))

                # write
                doc[relation] = rels
                resp = self.add_update_document(doc, uuid=uuid, token=token)
                return resp
            else:
                raise CatalogError('No document found with UUID {}'.format(uuid))
        except Exception as exc:
            raise

    def get_links(self, uuid, relation='child_of'):
        """Return list UUIDs for linked documents"""
        doc = self.query({'uuid': uuid})
        if doc is not None:
            if relation in list(doc.keys()):
                return doc.get(relation)
            if relation in list(self.schema['properties'].keys()):
                # The relationship could exist as per the schema but is not defined
                return list()
            else:
                raise CatalogError(
                    'Relationship "{}" not available in document {}'.format(
                        relation, uuid))

    def debug_mode(self):
        return debug_mode()

class StoreInterface(BaseStore):
    pass
