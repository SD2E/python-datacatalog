import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures import mongodb_settings, mongodb_authn
import datacatalog
from .data import challenge_problem, experiment

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/catalogmanager')

@pytest.fixture(scope='session')
def catalogmanager(mongodb_settings):
    return datacatalog.managers.catalog.CatalogManager(mongodb_settings)

def test_catman_discover_stores(mongodb_settings):
    base = datacatalog.managers.catalog.CatalogManager(mongodb_settings)

    # stores is a dict of store objected indexed by name
    assert isinstance(base.stores, dict)
    assert len(list(base.stores.keys())) > 0

    # check that they all have schemas
    for k, v in base.stores.items():
        assert isinstance(v.schema, dict)

def test_catman_get_uuidtype_invalid(catalogmanager):
    with pytest.raises(ValueError):
        tt = catalogmanager.get_uuidtype('102ea7b-6f98-bc04-c61e2efc8b44')
        # assert tt == '123'

@pytest.mark.parametrize("uuid,utype", [('1027aa77-d524-5359-a802-a8008adaecb5', 'experiment'),
                                        ('103246e1-bcdf-5b6e-a8dc-4c7e81b91141', 'sample'),
                                        ('10483e8d-6602-532a-8941-176ce20dd05a', 'measurement'),
                                        ('1055744d-7873-5a1f-ba29-8093d2e62ea6', 'file')])
def test_catman_get_uuidtype(uuid, utype, catalogmanager):
    # Test classification of UUID type
    tt = catalogmanager.get_uuidtype(uuid)
    assert tt == utype
    assert tt in catalogmanager.stores

@pytest.mark.parametrize("uuid,utype", [('1027aa77-d524-5359-a802-a8008adaecb5', 'experiment'),
                                        ('103246e1-bcdf-5b6e-a8dc-4c7e81b91141', 'sample'),
                                        ('10483e8d-6602-532a-8941-176ce20dd05a', 'measurement'),
                                        ('1055744d-7873-5a1f-ba29-8093d2e62ea6', 'file')])
def test_catman_get_by_uuid(uuid, utype, catalogmanager):
    """Check return by UUID
    """
    tt = catalogmanager.get_by_uuid(uuid)
    assert isinstance(tt, dict)

def test_catman_delete_by_uuid(catalogmanager):
    """Check delete doc and references by UUID"""
    deleted = catalogmanager.delete_by_uuid("1020797b-3af2-5cc0-b7ca-665de1ba8586")
    assert deleted is True

@pytest.mark.parametrize("identifier,success", [
    ('86753095', False),
    ('sample.tacc.20001', True),
    ('measurement.tacc.0xDEADBEEF', True),
    ('experiment.tacc.10001', True),
    ('Pipeline-Automation', True),
    ('1012da8b-663a-591f-a13d-cdf5277656a0', True)])
def test_catman_get_by_get_by_identifier(identifier, success, catalogmanager):
    """Check return document by text indentifer
    """
    tt = catalogmanager.get_by_identifier(identifier)
    if success is True:
        assert isinstance(tt, dict)
    else:
        assert tt is None

@pytest.mark.parametrize("uuids,success", [(
    ['1027aa77-d524-5359-a802-a8008adaecb5',
     '103246e1-bcdf-5b6e-a8dc-4c7e81b91141',
     '10483e8d-6602-532a-8941-176ce20dd05a'], True)])
def test_catman_get_by_uuids(uuids, success, catalogmanager):
    """Check return a list of UUIDs
    """
    tt = catalogmanager.get_by_uuids(uuids)
    if success is True:
        assert len(tt) == len(uuids)
