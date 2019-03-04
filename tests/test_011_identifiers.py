import os
import pytest
import sys
import yaml
import json
import jsonschema

from pprint import pprint
from . import longrun, delete, smoketest
from .data import identifiers
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_v1_v2_uuid_mapping():
    for utype, utext, v1uuid, v2uuid in identifiers.CASES:
        new_v2_uuid = datacatalog.identifiers.typeduuid.catalog_uuid_from_v1_uuid(v1uuid, utype)
        assert new_v2_uuid == v2uuid

def test_v1_v2_named_uuid_mapping():
    for utype, utext, v1uuid, v2uuid in identifiers.CASES:
        new_v2_uuid = datacatalog.identifiers.typeduuid.catalog_uuid(utext, utype)
        assert new_v2_uuid == v2uuid
