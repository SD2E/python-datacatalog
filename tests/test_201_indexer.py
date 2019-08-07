import os
import pytest
from datacatalog import managers

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
    base = managers.pipelinejobs.indexer.Indexer(
        mongodb_settings, agave=agave)
    if resolves:
        base.resolve_derived_references(refs, permissive=False)
    else:
        with pytest.raises(Exception):
            base.resolve_derived_references(refs, permissive=False)
