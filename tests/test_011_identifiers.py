import os
import pytest
from .data import identifiers
from datacatalog import identifiers as identifiers_module

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_v1_v2_uuid_mapping():
    for utype, utext, v1uuid, v2uuid in identifiers.CASES:
        new_v2_uuid = identifiers_module.typeduuid.catalog_uuid_from_v1_uuid(v1uuid, utype)
        assert new_v2_uuid == v2uuid

def test_v1_v2_named_uuid_mapping():
    for utype, utext, v1uuid, v2uuid in identifiers.CASES:
        new_v2_uuid = identifiers_module.typeduuid.catalog_uuid(utext, utype)
        assert new_v2_uuid == v2uuid
