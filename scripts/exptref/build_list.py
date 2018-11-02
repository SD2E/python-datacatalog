from __future__ import print_function

import os
import sys
import json

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from slugify import slugify
from tacconfig import config

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'

def get_drive_service(
        credential_path='token.json'):
    """Set up interface for interacting with Google Drive.

    Relies on credentials setup with setup.py
    """
    assert os.path.isfile(credential_path), (
        "Can't find credentials at " + credential_path)
    store = file.Storage(credential_path)
    credentials = store.get()
    assert credentials and not credentials.invalid, 'Must update credentials'
    http = credentials.authorize(Http())
    drive_service = build('drive', 'v3', http=http,
                                    cache_discovery=False)
    return drive_service


def get_files(filename, folder_id, drive_service=None):
    """Return a list of dicts representing the matches to the file."""
    if drive_service is None:
        drive_service = get_drive_service()
    response = drive_service.files().list(  # search for file
        q=("name contains '{}' "
           "and '{}' in parents "
           "and trashed=false").format(filename, folder_id),
        spaces='drive',
        fields='files(id, name)',
        includeTeamDriveItems=True,
        supportsTeamDrives=True).execute()
    return response['files']


def rationalize(textstring):
    sep = settings['slugify']['separator']
    return sep.join(slug for slug in slugify(
        textstring, stopwords=settings['slugify']['stopwords'],
        lowercase=settings['slugify']['case_insensitive']).split('-'))


settings = config.read_config()

records = []
for file in get_files('/', settings['google']['sheets_id']):
    key = rationalize(file['name'])
    if key != '':
        record = {'title': file['name'],
                'status': settings['schema']['default_status'],
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

with open('meta_experimental_requests.json', 'w+') as jout:
    json.dump(records, jout, indent=4)


ids = []
for rec in records:
    ids.append(rec['id'])

with open('experimental_requests_enum.json', 'w+') as sout:
    json.dump(sorted(ids), sout, indent=2)
