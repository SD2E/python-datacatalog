import pytest

@pytest.mark.smoktest
def test_agave_client_smoke(agave, credentials):
    resp = agave.profiles.get()
    assert isinstance(resp, dict)
    assert credentials['username'] == resp['username']
