import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from agavepy.agave import Agave

from .fixtures import agave, credentials
from . import longrun, delete

@longrun
def test_agave_client_smoke(agave, credentials):
    resp = agave.profiles.get()
    assert isinstance(resp, dict)
    assert credentials['username'] == resp['username']
