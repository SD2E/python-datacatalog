import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
from .fixtures.agave import agave, credentials
from agavepy.agave import Agave

import datacatalog
import transitions

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.mark.parametrize("refs, resolves", [
    (['/uploads/science-results1.xlsx', True]),
    (['105ffb0b-e4ad-50d1-841e-a985a600113d', True]),
    (['agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_WT/MG1655_WT.fa', True]),
    (['agave://data-sd2e-projects-users/sd2eadm/config.yml', True])
    ])
def test_indexer_resolve_derived_references(mongodb_settings,
                                            agave, refs, resolves):
    base = datacatalog.managers.pipelinejobs.indexer.Indexer(
        mongodb_settings, agave=agave)
    if resolves:
        base.resolve_derived_references(refs, permissive=False)
    else:
        with pytest.raises(Exception):
            base.resolve_derived_references(refs, permissive=False)
