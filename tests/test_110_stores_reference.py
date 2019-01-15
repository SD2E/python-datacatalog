import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
from .data import reference
from datacatalog.linkedstores.reference import ReferenceStore

def test_refs_db_init(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    assert base is not None

def test_refs_uuid_tytpe(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    assert base.get_uuid_type() == 'reference'

def test_refs_issue_uuid(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    uri = 'https://www.rcsb.org/structure/6N0V'
    identifier_string_uuid = base.get_typeduuid(uri, binary=False)
    assert identifier_string_uuid == '10900dfc-0d9f-5421-8ae7-6fba4d4ed795'

def test_refs_add(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    for uuid, doc in reference.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

@delete
def test_refs_delete(mongodb_settings):
    base = ReferenceStore(mongodb_settings)
    for uuid, doc in reference.DELETES:
        resp = base.delete_document(uuid)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
