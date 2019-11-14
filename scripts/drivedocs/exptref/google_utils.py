import os
import sys
import json
from google.oauth2 import service_account
import googleapiclient.discovery
from slugify import slugify

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

DEFAULT_TOKEN_PATH = os.path.join(HERE, 'token.json')
MANAGED_TOKEN_FILENAME = os.path.join(HERE, 'service_account.json')

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = os.path.join(HERE, 'service_account.json')

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


def __get_files(filename, folder_id, drive_service=None):
    """Return a list of dicts representing the matches to the file."""
    if drive_service is None:
        drive_service = get_drive_service()
    response = drive_service.files().list(  # search for file
        q=("name contains '{}' "
           "and '{}' in parents "
           "and trashed=false").format(filename, folder_id),
        spaces='drive',
        fields='files(id, name, size, modifiedTime, createdTime)',
        includeTeamDriveItems=True,
        orderBy='name',
        supportsTeamDrives=True).execute()
    return response['files']


def get_folders(filename, folder_id, drive_service=None):
    """Return a list of children for a folder."""
    if drive_service is None:
        drive_service = get_drive_service()
    response = drive_service.files().list(  # search for file
        q=("name contains '{}' "
           "and mimeType='application/vnd.google-apps.folder'"
           "and '{}' in parents "
           "and trashed=false").format(filename, folder_id),
        spaces='drive',
        fields='files(id, name, size, modifiedTime, createdTime)',
        includeTeamDriveItems=True,
        orderBy='name',
        supportsTeamDrives=True).execute()
    return response['files']


def get_files(filename, folder_id, drive_service=None):
    """Return a list of children for a folder."""
    if drive_service is None:
        drive_service = get_drive_service()
    response = drive_service.files().list(  # search for file
        q=("name contains '{}' "
           "and mimeType!='application/vnd.google-apps.folder'"
           "and '{}' in parents "
           "and trashed=false").format(filename, folder_id),
        spaces='drive',
        fields='files(id, name, size, modifiedTime, createdTime)',
        includeTeamDriveItems=True,
        orderBy='name',
        supportsTeamDrives=True).execute()
    return response['files']
class GoogleAPIError(Exception):
    pass
