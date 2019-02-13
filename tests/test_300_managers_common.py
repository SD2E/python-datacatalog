import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
from .fixtures.agave import agave, credentials
import datacatalog
import transitions
# from .data import managerscommon

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_mgr_common_get_stores(mongodb_settings, agave):
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    assert list(base.stores.keys()) != list()

def test_mgr_common_get_selfs_names(mongodb_settings, agave):
    inputs = ['/uploads/tacc/example/345.txt', '/uploads/tacc/example/123.txt', '0xCEFAEDFE.fastq']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    assert len(selfs) == 3

def test_mgr_common_get_selfs_w_ref(mongodb_settings, agave):
    inputs = ['/uploads/tacc/example/345.txt', '/uploads/tacc/example/123.txt', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_WT/MG1655_WT.fa']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    # test de-duplication and URI resolution work
    assert len(selfs) == 3

@pytest.mark.skipif(True, reason='deprecated in branch "file_id_not_identifier"')
def test_mgr_common_get_selfs_w_file_id(mongodb_settings, agave):
    inputs = ['file.biofab.10001']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    # test de-duplication and URI resolution work
    assert len(selfs) == 1

def test_mgr_common_get_selfs_w_agave_uri(mongodb_settings, agave):
    inputs = ['agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_WT/MG1655_WT.fa']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    # test de-duplication and URI resolution work
    assert len(selfs) == 1

def test_mgr_common_get_parents_names(mongodb_settings, agave):
    inputs = ['/uploads/tacc/example/345.txt', '/uploads/tacc/example/123.txt']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    parents = base.parent_from_inputs(inputs)
    # Test de-duplication since both inputs have same parent
    assert len(parents) == 1

# def test_mgr_common_get_derivation_names(mongodb_settings, agave):
#     inputs = ['/uploads/143209-H01.fcs', '/uploads/143209-A07.fcs', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_pTACmin/MG1655_pTACmin.interval_file']
#     base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
#     parents = base.derivation_from_inputs(inputs)
#     # This tests de-duplication since the two uploads have same parent
#     # It also tests the parent mapping for the reference case
#     assert len(parents) == 1

# def test_mgr_common_get_generator_names(mongodb_settings, agave):
#     inputs = ['/products/v1/41e1dec1-2940-5b04-bd9e-54af78f30774/aaf646a5-7c05-5ab3-a144-5563fca6830d/a4609424-508a-555c-9720-5ee3df44e777/whole-shrew-20181207T220030Z/output/output.csv', '/uploads/143209-A07.fcs', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_NAND_Circuit/MG1655_NAND_Circuit.interval_list']
#     base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
#     parents = base.generator_from_inputs(inputs)
#     # Only the long '/products' example should have a generated_by field
#     assert len(parents) == 1

@pytest.mark.skipif(True, reason='not valid now')
def test_mgr_common_lineage_file_short_exception(mongodb_settings, agave):
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    with pytest.raises(ValueError):
        # 10507438-f288-5898-9b72-68b31bcaff46's measurement has 90+ parents
        # so the traversal is expected to terminate at measurement
        base.lineage_from_uuid('10507438-f288-5898-9b72-68b31bcaff46', permissive=False)

@pytest.mark.skipif(True, reason='not valid now')
def test_mgr_common_lineage_file_short_truncated(mongodb_settings, agave):
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    # 10507438-f288-5898-9b72-68b31bcaff46's measurement has 90+ parents
    # so the traversal is expected to terminate at measurement
    resp = base.lineage_from_uuid(
        '10507438-f288-5898-9b72-68b31bcaff46', permissive=True)
    assert len(resp) == 2
    assert resp[1][0] == 'measurement'

@pytest.mark.skipif(True, reason='not valid now')
def test_mgr_common_lineage_level_from_lineage(mongodb_settings, agave):
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    # 10507438-f288-5898-9b72-68b31bcaff46's measurement has 90+ parents
    # so the traversal is expected to terminate at measurement
    lineage = base.lineage_from_uuid(
        '10507438-f288-5898-9b72-68b31bcaff46', permissive=True)
    assert base.level_from_lineage(lineage, level='file') == '10507438-f288-5898-9b72-68b31bcaff46'
    assert base.level_from_lineage(lineage, level='measurement') == '1040f664-0b71-54a6-8941-05ac277a6fa7'

def test_mgr_common_lineage_level_from_lineage_overrun(mongodb_settings, agave):
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    # 10507438-f288-5898-9b72-68b31bcaff46's measurement has 90+ parents
    # so the traversal is expected to terminate at measurement
    lineage = base.lineage_from_uuid(
        '10507438-f288-5898-9b72-68b31bcaff46', permissive=True)
    with pytest.raises(ValueError):
        base.level_from_lineage(lineage, level='sample')

def test_mgr_common_measurements_from_samples(mongodb_settings):
    samples = ['sample.tacc.20001']
    base = datacatalog.managers.common.Manager(mongodb_settings)
    result = base.measurements_from_samples(samples)
    assert len(result) == 3

def test_mgr_common_measurements_from_experiments(mongodb_settings):
    expts = ['experiment.tacc.10001']
    base = datacatalog.managers.common.Manager(mongodb_settings)
    result = base.measurements_from_experiments(expts)
    assert len(result) == 3

def test_mgr_common_measurements_from_designs(mongodb_settings):
    des = ['Pipeline-Automation']
    base = datacatalog.managers.common.Manager(mongodb_settings)
    result = base.measurements_from_designs(des)
    assert len(result) == 3

def test_mgr_common_measurements_from_challenges(mongodb_settings):
    cps = ['PIPELINE_AUTOMATION']
    base = datacatalog.managers.common.Manager(mongodb_settings)
    result = base.measurements_from_challenges(cps)
    assert len(result) == 3
