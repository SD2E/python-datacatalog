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
from .data import measurement

def test_meas_db(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)

def test_meas_db_list_collection_names(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    assert base.db.list_collection_names() is not None

def test_meas_schema(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_meas_name(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    assert base.name == 'measurements'

def test_meas_uuid_tytpe(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    assert base.get_uuid_type() == 'measurement'

def test_meas_issue_uuid(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    identifier_string = 'emerald.measurement.drastic-measures'
    identifier_string_uuid = base.get_typeduuid(identifier_string, binary=False)
    assert identifier_string_uuid == '10437f00-1722-5152-8e4f-683d0fba153a'

def test_meas_add(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    for key, doc, uuid_val in measurement.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None

def test_meas_update(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    for key, doc, uuid_val in measurement.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val)
        assert resp['uuid'] == uuid_val

@delete
def test_meas_delete(mongodb_settings):
    base = datacatalog.linkedstores.measurement.MeasurementStore(mongodb_settings)
    for key, doc, uuid_val in measurement.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}
