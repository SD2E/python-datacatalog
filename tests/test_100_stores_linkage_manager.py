import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete, smoketest, bootstrap

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from .fixtures.mongodb import mongodb_settings, mongodb_authn
import datacatalog
from .data import basestore

def test_linkages_get_linkages(mongodb_settings):
    """LinkedStore implements child_of but not acted_on
    """
    b = datacatalog.linkedstores.basestore.LinkedStore(mongodb_settings)
    links = b.get_linkages()
    assert len(list(links.keys())) > 0, 'Empty get_linkages()'
    assert 'child_of' in links.keys(), 'Store must allow child_of linkage'
    assert 'acted_on' not in links.keys(), 'Store does not allow that linkage'

def test_linkages_get_linkages_override_subclass(mongodb_settings):
    """PipelineJobStore includes an 'acted_on' linkage
    """
    b = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_settings)
    links = b.get_linkages()
    assert len(list(links.keys())) > 0, 'Empty get_linkages()'
    assert 'child_of' in links.keys(), 'Store must allow child_of linkage'
    assert 'acted_on' in links.keys(), 'Store must allow acted_on linkage'
    assert 'acted_using' in links.keys(), 'Store must allow acted_on linkage'
    assert 'derived_from' not in links.keys(), 'Store does not allow that linkage'
    assert 'derived_using' not in links.keys(), 'Store does not allow that linkage'

def test_linkages_exd_add_link_one(mongodb_settings):
    d = datacatalog.linkedstores.experiment_design.ExperimentDesignStore(mongodb_settings)
    d.add_link('114bb9f2-1483-5195-9dd6-78ea91b70291', '1012da8b-663a-591f-a13d-cdf5277656a0', relation='child_of')

def test_linkages_exd_add_link_too_many(mongodb_settings):
    d = datacatalog.linkedstores.experiment_design.ExperimentDesignStore(mongodb_settings)
    with pytest.raises(Exception):
        d.add_link('114bb9f2-1483-5195-9dd6-78ea91b70291',
                ['10116a04-35ed-5ba1-ae07-da45c0ca9e6f', '101ada00-0107-5f88-80d5-ea16eab97de5'], relation='child_of')

def test_linkages_exd_add_link_replace(mongodb_settings):
    d = datacatalog.linkedstores.experiment_design.ExperimentDesignStore(mongodb_settings)
    d.add_link('114bb9f2-1483-5195-9dd6-78ea91b70291', '10158eb6-edf4-589f-ad2a-496e50e7eff5', relation='child_of')



# def test_files_links_add_link(mongodb_settings):
#     base = FileStore(mongodb_settings)
#     for key, doc, uuid_val in file.UPDATES:
#         resp = base.add_link(uuid_val, '1040f664-a654-0b71-4189-2ac6f77a05a7', 'child_of')
#         assert resp is True
#         links = base.get_links(uuid_val, 'child_of')
#         assert '1040f664-a654-0b71-4189-2ac6f77a05a7' in links

# def test_files_links_add_link(mongodb_settings):
#     base = FileStore(mongodb_settings)
#     for key, doc, uuid_val in file.UPDATES:
#         resp = base.add_link(uuid_val, ['1040f664-a654-0b71-4189-2ac6f77a05a7', '104dae4d-a677-5991-ae1c-696d2ee9884e',
#         '10483e8d-6602-532a-8941-176ce20dd05a'], 'child_of')
#         assert resp is True
#         links = base.get_links(uuid_val, 'child_of')
#         assert '1040f664-a654-0b71-4189-2ac6f77a05a7' in links

# def test_files_links_remove_link(mongodb_settings):
#     base = FileStore(mongodb_settings)
#     for key, doc, uuid_val in file.UPDATES:
#         resp = base.remove_link(uuid_val, '104dae4d-a677-5991-ae1c-696d2ee9884e')
#         assert resp is True
#         links = base.get_links(uuid_val, 'child_of')
#         assert '104dae4d-a677-5991-ae1c-696d2ee9884e' not in links

# def test_files_links_add_invalid_linkage(mongodb_settings):
#     base = FileStore(mongodb_settings)
#     for key, doc, uuid_val in file.UPDATES:
#         resp = base.add_link(uuid_val, '1040f664-a654-0b71-4189-2ac6f77a05a7', 'acted_on')
#         assert resp is False
