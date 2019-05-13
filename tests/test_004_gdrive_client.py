import os
import pytest
import sys
import yaml
import json
from agavepy.agave import Agave
from pprint import pprint
from . import longrun, delete, networked, bootstrap
from .googleapi import google_drive, google_sheets_id, google_sheets_dir
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@bootstrap
def test_gdrive_smoke(google_drive, google_sheets_id, google_sheets_dir):
    g = google_drive
    files = g.get_files(google_sheets_dir, google_sheets_id)
    assert isinstance(files, list), 'Failed to return a list of "file" objects'
    assert 'id' in files[0], 'List had no apparent "file" objects'
