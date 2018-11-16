from __future__ import print_function

import os
import sys
import json
from google.oauth2 import service_account
import googleapiclient.discovery

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'

def get_drive_service(credential_path=SERVICE_ACCOUNT_FILE, scopes=SCOPES):
    """Set up interface for interacting with Google Drive.

    Relies on service account credentials
    """
    assert os.path.isfile(credential_path), (
        "Can't find credentials at " + credential_path)
    credentials = service_account.Credentials.from_service_account_file(
        credential_path, scopes=scopes)
    service = googleapiclient.discovery.build(
        'drive', 'v3', credentials=credentials)
    return service


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
