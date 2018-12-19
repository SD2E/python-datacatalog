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

def test_mgr_common_get_derivs(mongodb_settings, agave):
    inputs = ['/uploads/143209-H01.fcs', '/uploads/143209-A07.fcs', '0xCEFAEDFE.fastq']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    derivs = base.derivation_from_inputs(inputs)
    # test de-duplication since the two uploads have same child_of
    assert len(derivs) == 2

def test_mgr_common_get_derivs_w_ref(mongodb_settings, agave):
    inputs = ['/uploads/143209-H01.fcs', '/uploads/143209-A07.fcs', '0xCEFAEDFE.fastq', 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_NAND_Circuit/MG1655_NAND_Circuit.fa']
    base = datacatalog.managers.common.Manager(mongodb_settings, agave=agave)
    derivs = base.derivation_from_inputs(inputs)
    # test de-duplication since the two uploads have same child_of
    assert len(derivs) == 2
