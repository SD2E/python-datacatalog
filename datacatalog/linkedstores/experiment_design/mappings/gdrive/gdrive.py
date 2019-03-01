import os
import json
import validators
from attrdict import AttrDict
from pprint import pprint
from slugify import slugify
from . import google_utils
from .errors import GoogleSheetsError, IncorrectConfiguration, \
    MappingNotFound, UnsupportedMapping

DEFAULT_TOKEN_PATH = 'token.json'
MANAGED_TOKEN_FILENAME = 'service_account.json'

class ExperimentReferenceMapping(object):
    """Synchronizable mapping between ExperimentDesign and a Google Document
    """

    def __init__(self, mapper_config, google_client=None, google_client_path=None):
        """Initialize connection to Google Drive API

        Args:
            mapper_config (dict): A structured configuration dictionary
            google_client (dict, optional): A structured dictionary containing API credentials
            google_client_path (str, optional): Filesystem path to a file containing API credentials

        Raises:
            IncorrectConfiguration: Raised when `mapper_config` is incorrect

        """
        self.config = None
        """Value passed for mapping_config"""
        self.token = None
        """Google API client"""
        self.tokenpath = None
        """Path to API credentials file"""
        self.filescache = []
        """Cached lookups from Google Drive API queries"""
        self.failures = []
        """Cache of failed Google Drive API query responses"""
        self.ready = False
        """Semaphore marking the Google Drive API client as ready"""

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
        """Populate the mapping cache

        This must be done explicitly after `__init__`` to avoid thrashing the
        API client.

        Raises:
            GoogleSheetsError: Occurs if connection or query to Google fails

        Returns:
            object: Returns `self` so that `populate` can be chained to another service call
        """
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
            # pprint('files_listing', files_listing)
            self.filescache = self.encode_files(files_listing)
        except Exception as exc:
            raise GoogleSheetsError('Error fetching file listing', exc)

        # Now, we are ready to map between datacatalog and google!
        self.ready = True
        return self

    def encode_files(self, files_listing):
        """Transform a Google Drive listing into ExperimentDesigns

        Args:
            files_listing (list): a listing from Google files API v3

        Returns:
            list: List of ExperimentDesign `dict` objects
        """
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

    def encode_title_as_id(self, textstring, stopwords=[], separator='-'):
        """Transform Google Document title into an identifier

        Args:
            textstring (str): The title of a document
            stopwords (list, optional): List of stopwords to filter from encoded identifier
            separator (str, optional): Separator character for joining slugified words

        Returns:
            str: The slugified version of `textstring`
        """
        sep = self.config['slugify'].get('separator', separator)
        stops = self.config['slugify'].get('stopwords', []).extend(stopwords)
        return sep.join(slug for slug in slugify(
            textstring, stopwords=stops,
            lowercase=self.config['slugify']['case_insensitive']).split('-'))

    def uri_to_key(self, uri, keyname):
        """Get the value for a key associated with a reference URI

        Args:
            uri (str): One of the known set of Google Drive document URIs
            keyname (str): The name of the key whose value will be returned

        Raises:
            UnsupportedMapping: Occurs when `uri` is not a valid URI or `keyname` does not exist in document
            MappingNotFound: Occurs when mapping is not successful

        Returns:
            object: The value of `keyname` in the ExperimentMapping identifier by `uri`
        """
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
        """Get the title associated with a reference URI"""
        return self.uri_to_key(uri, 'title')

    def uri_to_id(self, uri):
        """Get the document identifier associated with a reference URI"""
        return self.uri_to_key(uri, 'id')

    def id_to_key(self, id, keyname):
        """Get the value for a key associated with a given identifier

        Args:
            id (str): One of the known set of document identifiers
            keyname (str): The name of the key whose value will be returned

        Raises:
            UnsupportedMapping: Occurs when `keyname` does not exist in the document
            MappingNotFound: Occurs when `id` is not known

        Returns:
            object: The value of `keyname` in the ExperimentMapping identifier by `id`
        """
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
        """Get the URI associated with an identifier"""
        return self.id_to_key(id, 'uri')

    def id_to_title(self, id):
        """Get the human-readable title associated with an identifier"""
        return self.id_to_key(id, 'title')

    def title_to_uri(self, title):
        raise UnsupportedMapping('Not a supported mapping')

    def title_to_id(self, title):
        raise UnsupportedMapping('Not a supported mapping')
