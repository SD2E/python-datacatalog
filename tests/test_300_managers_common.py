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
    inputs = ['/uploads/143209-H01.fcs', '/uploads/143209-A07.fcs', '0xCEFAEDFE.fastq']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    # test de-duplication since the two uploads have same child_of
    assert len(selfs) == 3

def test_mgr_common_get_selfs_w_ref(mongodb_settings, agave):
    inputs = ['/uploads/143209-H01.fcs', '/uploads/143209-A07.fcs', '0xCEFAEDFE.fastq', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_NAND_Circuit/MG1655_NAND_Circuit.interval_list']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    # test de-duplication and URI resolution work
    assert len(selfs) == 4

def test_mgr_common_get_selfs_w_file_id(mongodb_settings, agave):
    inputs = ['biofab.file.100']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    # test de-duplication and URI resolution work
    assert len(selfs) == 1

def test_mgr_common_get_selfs_w_agave_uri(mongodb_settings, agave):
    inputs = ['agave://data-sd2e-community/uploads/143209-H01.fcs']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    selfs = base.self_from_inputs(inputs)
    # test de-duplication and URI resolution work
    assert len(selfs) == 1

def test_mgr_common_get_parents_names(mongodb_settings, agave):
    inputs = ['/uploads/143209-H01.fcs', '/uploads/143209-A07.fcs', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_NAND_Circuit/MG1655_NAND_Circuit.interval_list']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    parents = base.parent_from_inputs(inputs)
    # This tests de-duplication since the two uploads have same parent
    # It also tests the parent mapping for the reference case
    assert len(parents) == 2

def test_mgr_common_get_derivation_names(mongodb_settings, agave):
    inputs = ['/uploads/143209-H01.fcs', '/uploads/143209-A07.fcs', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_NAND_Circuit/MG1655_NAND_Circuit.interval_list']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    parents = base.derivation_from_inputs(inputs)
    # This tests de-duplication since the two uploads have same parent
    # It also tests the parent mapping for the reference case
    assert len(parents) == 0

def test_mgr_common_get_generator_names(mongodb_settings, agave):
    inputs = ['/products/v2/1022efa34480538fa581f1810fb4e0c3/106bd127e2d257acb9be11ed06042e68/sample.uw_biofab.141715_MG1655_pJS007_LALT__backbone_replicate_2_time_5:hours_temp_37.0_arabinose_0_mM_IPTG_0.25_mM.rnaseq.original.bwa.sorted.sam', '/uploads/143209-A07.fcs', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_NAND_Circuit/MG1655_NAND_Circuit.interval_list']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    parents = base.generator_from_inputs(inputs)
    # Only the long '/products' example should have a generated_by field
    assert len(parents) == 1

def test_mgr_common_lineage_file_short_exception(mongodb_settings, agave):
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    with pytest.raises(ValueError):
        # 10507438-f288-5898-9b72-68b31bcaff46's measurement has 90+ parents
        # so the traversal is expected to terminate at measurement
        base.lineage_from_uuid('10507438-f288-5898-9b72-68b31bcaff46')

def test_mgr_common_lineage_file_short_truncated(mongodb_settings, agave):
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    # 10507438-f288-5898-9b72-68b31bcaff46's measurement has 90+ parents
    # so the traversal is expected to terminate at measurement
    resp = base.lineage_from_uuid(
        '10507438-f288-5898-9b72-68b31bcaff46', permissive=True)
    assert len(resp) == 2
    assert resp[1][0] == 'measurement'

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
