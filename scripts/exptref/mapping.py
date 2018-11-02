import arrow
import datetime
import os
import json
import sys
import validators
from attrdict import AttrDict
from slugify import slugify
from .google_utils import GoogleAPIError
from . import google_utils

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

DEFAULT_TOKEN_PATH = os.path.join(HERE, 'token.json')
MANAGED_TOKEN_FILENAME = os.path.join(HERE, 'service_account.json')

class ExperimentReferenceMapping(object):
    def __init__(self, mapper_config, google_client=None, google_client_path=None):

        if isinstance(mapper_config, dict):
            self.config = mapper_config
        else:
            raise ValueError('"mapper_config" is expected to be a dict')

        self.token = None
        # Read from client token in PWD
        if os.path.exists(MANAGED_TOKEN_FILENAME):
            try:
                self.token = json.load(MANAGED_TOKEN_FILENAME)
            except Exception:
                pass
        # if a google client is passed in the constructor, load it instead
        # and also write it out to cwd()
        if isinstance(google_client, dict):
            self.token = google_client
            with open(MANAGED_TOKEN_FILENAME, 'w') as tokenfile:
                json.dump(dict(self.token), tokenfile, indent=4)
                self.tokenpath = os.path.abspath(MANAGED_TOKEN_FILENAME)
        else:
            # attempt to read from a specified path
            self.token = self.__read_token_from_file(path=google_client_path)
        self.filescache = []
        self.failures = []
        self.ready = False

    def __read_token_from_file(self, path):
        if self.token is None:
            if os.path.exists(path):
                try:
                    self.token = json.load(open(path, 'r'))
                    self.tokenpath = os.path.abspath(path)
                except Exception as exc:
                    raise GoogleAPIError(
                        'A Google client was not provided and no token could be loaded from {}'.format(path), exc)
            else:
                raise GoogleAPIError('A Google client was not provided and no token file was specified')
        return self

    def populate(self):
        """Populate lookup cache. We do not do this at init() time to
        avoid thrashing the API client during testing"""
        # Init the drive service and cache it
        try:
            self._drive_service = google_utils.get_drive_service(
                credential_path=self.tokenpath)
        except Exception as exc:
            raise GoogleAPIError('Failed to get Google Drive service', exc)

        # Init the files listing
        try:
            files_listing = google_utils.get_files(
                self.config['google_sheets_dir'],
                self.config['google_sheets_id'],
                self._drive_service)
            # print('files_listing', files_listing)
            self.filescache = self.encode_files(files_listing)
        except Exception as exc:
            raise GoogleAPIError('Error fetching file listing', exc)

        self.ready = True
        return self

    def generate_schema_definitions(self):
        doc = {'description': 'Experiment reference enumeration',
               'type': 'string',
               'enum': []}
        for rec in self.filescache:
            doc['enum'].append(rec['experiment_id'])
        return doc

    def encode_files(self, files_listing):
        records = []
        for file in files_listing:
            key = self.encode_title_as_id(file['name'])
            if key != '':
                record = {'title': file['name'],
                          'status': self.config['schema_default_status'],
                          'uri': 'https://docs.google.com/document/d/{}'.format(file['id']),
                          'experiment_id': key,
                          'created': google_time_to_datetime(file['createdTime']),
                          'updated': google_time_to_datetime(file['modifiedTime']),
                          'child_of': []}
                records.append(record)
        # Placeholder for Unknown mapping
        unknown_rec = {'title': 'Undefined Experiment Request',
                       'status': 'DRAFT',
                       'uri': None,
                       'experiment_id': 'Unknown',
                       'type': 'experiment_reference',
                       'created': datetime.datetime.utcnow(),
                       'updated': datetime.datetime.utcnow(),
                       'child_of': []}
        records.append(unknown_rec)
        return records

    def encode_title_as_id(self, textstring):
        sep = self.config['slugify']['separator']
        return sep.join(slug for slug in slugify(
            textstring, stopwords=self.config['slugify']['stopwords'],
            lowercase=self.config['slugify']['case_insensitive']).split('-'))

    def uri_to_key(self, uri, keyname):
        if not validators.url(uri, public=True):
            raise ValueError('Not a valid URI: {}'.format(uri))
        # filter Google's useless terminal slash-param
        uri = uri.replace('/edit?usp=sharing', '')
        for cached in self.filescache:
            if cached['uri'] == uri:
                try:
                    return cached[keyname]
                except KeyError:
                    raise ValueError('Mapping URI to {} is not supported'.format(keyname))
        raise ValueError('{} does not resolve to a {}'.format(uri, keyname))

    def uri_to_title(self, uri):
        return self.uri_to_key(uri, 'title')

    def uri_to_id(self, uri):
        return self.uri_to_key(uri, 'experiment_id')

    def id_to_key(self, id, keyname):
        for cached in self.filescache:
            if cached['experiment_id'] == id:
                try:
                    return cached[keyname]
                except KeyError:
                    raise ValueError(
                        'Mapping id {} to {} is not supported'.format(id, keyname))
        raise ValueError(
            '{} does not resolve to a {}'.format(id, keyname))

    def id_to_uri(self, id):
        return self.id_to_key(id, 'uri')

    def id_to_title(self, id):
        return self.id_to_key(id, 'title')

    def title_to_uri(self, title):
        raise ValueError('Not a supported mapping')

    def title_to_id(self, title):
        raise ValueError('Not a supported mapping')

def google_time_to_datetime(timestring):
    return datetime.datetime.utcfromtimestamp(arrow.get(timestring).timestamp)
