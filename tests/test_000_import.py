import os
import pytest
import sys

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_can_import_datacalog():
    import datacatalog
