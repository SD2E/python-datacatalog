import os
import sys
import json
import pytest
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

class GoogleAPIError(Exception):
    """Error occurred working with a Google REST API"""
    pass


class GoogleDriveHelper(object):
    """Interface for interacting with Google Drive.

    Args:
        credential_path (str): Path to ``service_account.json``
        scopes (list, optional): Set of Oauth scopes
    """

    def __init__(self,
                 credential_path=SERVICE_ACCOUNT_FILE,
                 scopes=SCOPES):
        self.__setup(credential_path, scopes)

    def __setup(self, credential_path, scopes):
        try:
            assert os.path.isfile(credential_path), (
                "Can't find credentials at " + credential_path)
            credentials = service_account.Credentials.from_service_account_file(
                credential_path, scopes=scopes)
            service = googleapiclient.discovery.build(
                'drive', 'v3', credentials=credentials)
            setattr(self, 'service', service)
        except Exception as exc:
            raise GoogleAPIError("Google Drive API setup failed", exc)
        return self

    def get_folders(self, filename, folder_id, drive_service=None):
        """Return a list of children for a folder."""
        try:
            response = self.service.files().list(  # search for file
                q=("name contains '{}' "
                   "and mimeType='application/vnd.google-apps.folder'"
                   "and '{}' in parents "
                   "and trashed=false").format(filename, folder_id),
                spaces='drive',
                fields='files(id, name, size, modifiedTime, createdTime)',
                includeTeamDriveItems=True,
                supportsTeamDrives=True).execute()
            return response['files']
        except Exception as exc:
            raise GoogleAPIError("Google Drive API get_folders failed", exc)

    def get_files(self, filename, folder_id, drive_service=None):
        """Return a list of children for a folder."""
        try:
            response = self.service.files().list(  # search for file
                q=("name contains '{}' "
                   "and mimeType!='application/vnd.google-apps.folder'"
                   "and '{}' in parents "
                   "and trashed=false").format(filename, folder_id),
                spaces='drive',
                fields='files(id, name, size, modifiedTime, createdTime)',
                includeTeamDriveItems=True,
                supportsTeamDrives=True).execute()
            return response['files']
        except Exception as exc:
            raise GoogleAPIError("Google Drive API get_files failed", exc)
