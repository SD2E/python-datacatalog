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
from data import challenge_problem

sys.path.insert(0, '/')
import datacatalog

def test_cp_db(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)

def test_cp_db_list_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    assert base.db.list_collection_names() is not None

def test_cp_schema(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_cp_name(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    assert base.name == 'challenges'

def test_cp_uuid_tytpe(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    assert base.get_uuid_type() == 'challenge_problem'

def test_cp_issue_uuid(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    identifier_string = 'DRAKE_EQUATION'
    identifier_string_uuid = base.get_typed_uuid(identifier_string, binary=False)
    assert identifier_string_uuid == '1010c127-7f30-5ac0-8f6f-2ebcca0a0c06'

def test_cp_add(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    for key, doc, uuid_val in challenge_problem.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] == uuid_val

def test_cp_update(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    for key, doc, uuid_val in challenge_problem.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

def test_cp_delete(mongodb_settings):
    base = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb_settings)
    for key, doc, uuid_val in challenge_problem.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
