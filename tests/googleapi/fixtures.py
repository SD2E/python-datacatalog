import os
import sys
import json
import pytest
from google.oauth2 import service_account
import googleapiclient.discovery
from .common import GoogleDriveHelper

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

__all__ = ["google_service_account_file",
           "google_sheets_id",
           "google_sheets_dir",
           "google_drive"]

@pytest.fixture(scope='session')
def google_service_account_file(service_account_file=None):
    if service_account_file is None:
        service_account_file = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE', os.path.join(HERE, 'service_account.json'))
    if os.path.exists(service_account_file):
        return service_account_file
    else:
        raise OSError('No service account file was accessible')

@pytest.fixture(scope='session')
def google_sheets_id(google_sheets_id=None):
    if google_sheets_id is None:
        google_sheets_id = os.environ.get('GOOGLE_SHEETS_ID',
                                          '0BwJXMnMq5iNMbWFqVUhwOHpzcVE')
    return google_sheets_id

@pytest.fixture(scope='session')
def google_sheets_dir(google_sheets_dir=None):
    if google_sheets_dir is None:
        google_sheets_dir = os.environ.get('GOOGLE_SHEETS_DIR', '/')
    return google_sheets_dir

@pytest.fixture(scope='session')
def google_drive(google_service_account_file, scopes=SCOPES):
    return GoogleDriveHelper(google_service_account_file, scopes)
