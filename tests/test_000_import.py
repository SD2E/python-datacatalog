import os
import pytest
import sys
from . import longrun, delete, bootstrap, smoketest

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@smoketest
def test_can_import_datacalog():
    import datacatalog
