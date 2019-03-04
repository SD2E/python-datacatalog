import os
import json
import validators
from attrdict import AttrDict
from slugify import slugify
from .errors import *
from . import google_utils

DEFAULT_TOKEN_PATH = 'token.json'
MANAGED_TOKEN_FILENAME = 'service_account.json'

class ExperimentReferenceMapping(object):
    def __init__(self, mapper_config, google_client=None, google_client_path=None):
        if isinstance(mapper_config, dict):
            self.config = mapper_config
        else:
            raise IncorrectConfiguration('"mapper_config" is expected to be a dict')

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
                    raise GoogleSheetsError(
                        'A Google client was not provided and no token could be loaded from {}'.format(path), exc)
            else:
                raise GoogleSheetsError('A Google client was not provided and no token file was specified')
        return self

    def populate(self):
        """Populate lookup cache. We do not do this at init() time to
        avoid thrashing the API client during testing"""
        # Init the drive service and cache it
        try:
            self._drive_service = google_utils.get_drive_service(
                credential_path=self.tokenpath)
        except Exception as exc:
            raise GoogleSheetsError('Failed to get Google Drive service', exc)

        # Init the files listing
        try:
            files_listing = google_utils.get_files(
                self.config['google_sheets_dir'],
                self.config['google_sheets_id'],
                self._drive_service)
            # print('files_listing', files_listing)
            self.filescache = self._encode_files(files_listing)
        except Exception as exc:
            raise GoogleSheetsError('Error fetching file listing', exc)

        self.ready = True
        return self

    def _encode_files(self, files_listing):
        records = []
        for file in files_listing:
            key = self.encode_title_as_id(file['name'])
            if key != '':
                record = {'title': file['name'],
                          'status': self.config['schema_default_status'],
                          'uri': 'https://docs.google.com/document/d/{}'.format(file['id']),
                          'id': key,
                          'type': 'experiment_reference'}
                records.append(record)
        # Placeholder for Unknown mapping
        unknown_rec = {'title': 'Unknown Experiment Request',
                       'status': None,
                       'uri': None,
                       'id': 'Unknown',
                       'type': 'experiment_reference'}
        records.append(unknown_rec)
        return records

    def encode_title_as_id(self, textstring):
        sep = self.config['slugify']['separator']
        return sep.join(slug for slug in slugify(
            textstring, stopwords=self.config['slugify']['stopwords'],
            lowercase=self.config['slugify']['case_insensitive']).split('-'))

    def __uri_to_key(self, uri, keyname):
        if not validators.url(uri, public=True):
            raise UnsupportedMapping('Not a valid URI: {}'.format(uri))
        # filter Google's useless terminal slash-param
        uri = uri.replace('/edit?usp=sharing', '')
        for cached in self.filescache:
            if cached['uri'] == uri:
                try:
                    return cached[keyname]
                except KeyError:
                    raise UnsupportedMapping('Mapping URI to {} is not supported'.format(keyname))
        raise MappingNotFound('{} does not resolve to a {}'.format(uri, keyname))

    def uri_to_title(self, uri):
        return self.__uri_to_key(uri, 'title')

    def uri_to_id(self, uri):
        return self.__uri_to_key(uri, 'id')

    def __id_to_key(self, id, keyname):
        for cached in self.filescache:
            if cached['id'] == id:
                try:
                    return cached[keyname]
                except KeyError:
                    raise UnsupportedMapping(
                        'Mapping id {} to {} is not supported'.format(id, keyname))
        raise MappingNotFound(
            '{} does not resolve to a {}'.format(id, keyname))

    def id_to_uri(self, id):
        return self.__id_to_key(id, 'uri')

    def id_to_title(self, id):
        return self.__id_to_key(id, 'title')

    def title_to_uri(self, title):
        raise UnsupportedMapping('Not a supported mapping')

    def title_to_id(self, title):
        raise UnsupportedMapping('Not a supported mapping')

