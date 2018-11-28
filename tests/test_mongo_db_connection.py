import os
import pytest
import sys
import yaml
import json

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
from fixtures.mongodb import mongodb_settings, mongodb_authn

sys.path.insert(0, '/')
import datacatalog

def test_db_connection_settings_smoke(mongodb_settings):
    """MongoDb connection can be made with settings dict"""
    db = datacatalog.mongo.db_connection(mongodb_settings)
    colls = db.list_collection_names()
    assert colls is not None

def test_db_connection_authn_smoke(mongodb_authn):
    """MongoDb connection can be made with auth string"""
    db = datacatalog.mongo.db_connection(mongodb_authn)
    colls = db.list_collection_names()
    assert colls is not None
