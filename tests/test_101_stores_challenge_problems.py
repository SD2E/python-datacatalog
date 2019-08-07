import pytest
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog import linkedstores
from datacatalog.linkedstores.challenge_problem import ChallengeStore
from .data import challenge_problem

def test_cp_db_init(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    assert base is not None

def test_cp_db_heritable_schema(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    assert 'title' in base.get_indexes()

def test_cp_schema(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_cp_name(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    assert base.name == 'challenges'

def test_cp_uuid_tytpe(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    assert base.get_uuid_type() == 'challenge_problem'

def test_cp_issue_uuid(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    identifier_string = 'INVALIDATE_DRAKE_EQUATION'
    identifier_string_uuid = base.get_typeduuid(identifier_string, binary=False)
    assert identifier_string_uuid == '101b226b-c7e1-51e5-815e-3bdc633b5ed5'

def test_cp_add(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    for key, doc, uuid_val in challenge_problem.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] == uuid_val

def test_cp_update(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    for key, doc, uuid_val in challenge_problem.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

@pytest.mark.delete
def test_cp_delete(mongodb_settings):
    base = ChallengeStore(mongodb_settings)
    for key, doc, uuid_val in challenge_problem.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
