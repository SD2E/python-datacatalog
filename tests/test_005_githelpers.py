import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
import datacatalog

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_get_sha1():
    githash = datacatalog.githelpers.get_sha1()
    assert isinstance(githash, str)
    assert len(githash) == 40

def test_get_sha1_short():
    githash = datacatalog.githelpers.get_sha1_short()
    assert isinstance(githash, str)
    assert len(githash) == 7

def test_get_remote_uri():
    """Inspect repo for its `remote`

    Todo:
        - Validate returned value
    """
    giturl = datacatalog.githelpers.get_remote_uri()
    assert giturl is not None
