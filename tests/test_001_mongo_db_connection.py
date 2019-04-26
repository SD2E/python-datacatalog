import os
import pytest
import sys
import yaml
import json

import datacatalog
from fixtures.mongodb import mongodb_settings, mongodb_authn
from . import longrun, delete, bootstrap, smoketest

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@smoketest
def test_db_connection_settings(mongodb_settings):
    """MongoDb connection can be made with settings dict"""
    db = datacatalog.mongo.db_connection(mongodb_settings)
    colls = db.list_collection_names()
    assert colls is not None

@smoketest
def test_db_connection_authn(mongodb_authn):
    """MongoDb connection can be made with auth string"""
    db = datacatalog.mongo.db_connection(mongodb_authn)
    colls = db.list_collection_names()
    assert colls is not None
