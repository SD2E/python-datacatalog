# from . import data

import os
import pytest
import sys

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

if PARENT not in sys.path:
    sys.path.insert(0, PARENT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# https://stackoverflow.com/a/43938191
#
# from . import longrun
#
# @longrun
# def test_long():
#   pass

bootstrap = pytest.mark.skipif(
    not pytest.config.option.bootstrap,
    reason="needs --bootstrap option to run")

longrun = pytest.mark.skipif(
    not pytest.config.option.longrun,
    reason="needs --longrun option to run")

delete = pytest.mark.skipif(
    not pytest.config.option.delete,
    reason="needs --delete option to run")

networked = pytest.mark.skipif(
    not pytest.config.option.networked,
    reason="needs --networked option to run")
