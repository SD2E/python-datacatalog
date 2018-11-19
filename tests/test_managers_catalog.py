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

@pytest.mark.parametrize("uuid,utype", [('102e742e-e67a-5e99-bc04-c60d1eec9a41', 'experiment'),
                                        ('1039c6df-4f48-5a2e-967c-5881401eb8c3', 'sample'),
                                        ('1040f664-0b71-54a6-8941-05ac277a6fa7', 'measurement'),
                                        ('10507438-f288-5898-9b72-68b31bcaff46', 'file')])
def test_catman_get_uuidtype(uuid, utype, catalogmanager):
    # Test classification of UUID type
    tt = catalogmanager.get_uuidtype(uuid)
    assert tt == utype
    assert tt in catalogmanager.stores

@pytest.mark.parametrize("uuid,utype", [('102e742e-e67a-5e99-bc04-c60d1eec9a41', 'experiment'),
                                        ('1039c6df-4f48-5a2e-967c-5881401eb8c3', 'sample'),
                                        ('1040f664-0b71-54a6-8941-05ac277a6fa7', 'measurement'),
                                        ('10507438-f288-5898-9b72-68b31bcaff46', 'file')])
def test_catman_get_by_uuid(uuid, utype, catalogmanager):
    # Test classification of UUID type
    tt = catalogmanager.get_by_uuid(uuid)
    assert isinstance(tt, dict)

def test_catman_delete_by_uuid(catalogmanager):
    # Test classification of UUID type
    deleted = catalogmanager.delete_by_uuid("10300633-da8f-5a45-89b1-f497de5c7ca8")
    assert deleted is True
