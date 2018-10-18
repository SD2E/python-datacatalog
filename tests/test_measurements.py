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
from data import measurements

sys.path.insert(0, '/')
import datacatalog

def test_exp_db(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)

def test_exp_db_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    assert base.db.collection_names() is not None

def test_exp_schema(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_exp_name(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    assert base.name == 'measurements'

def test_exp_uuid_tytpe(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    assert base.get_uuid_type() == 'measurement'

def test_exp_issue_uuid(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    identifier_string = 'emerald.measurement.drastic-measures'
    identifier_string_uuid = base.get_typed_uuid(identifier_string, binary=False)
    assert identifier_string_uuid == '10437f00-1722-5152-8e4f-683d0fba153a'

def test_exp_add(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    for key, doc, uuid_val in measurements.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

def test_exp_update(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    for key, doc, uuid_val in measurements.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

def test_exp_delete(mongodb_settings):
    base = datacatalog.linkedstores.measurements.MeasurementStore(mongodb_settings)
    for key, doc, uuid_val in measurements.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp == {'n': 1, 'ok': 1.0}
