import pytest
from datacatalog import githelpers

@pytest.mark.smoktest
def test_get_sha1():
    githash = githelpers.get_sha1()
    assert isinstance(githash, str)
    assert len(githash) == 40

def test_get_sha1_short():
    githash = githelpers.get_sha1_short()
    assert isinstance(githash, str)
    assert len(githash) == 7

def test_get_remote_uri():
    """Inspect repo for its `remote`

    Todo:
        - Validate returned value
    """
    giturl = githelpers.get_remote_uri()
    assert giturl is not None
