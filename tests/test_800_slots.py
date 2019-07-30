import os
import pytest
import sys
import yaml
import json
import inspect
import warnings
from pprint import pprint

from . import longrun, delete
from .fixtures import agave, credentials

from datacatalog import slots
from datacatalog.identifiers import random_string

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_slot_create(agave):
    """Confirm that slot is not 'ready' after creation
    """
    p = slots.client.Slot(agave=agave)
    p.create()
    assert p.name is not None
    assert p.ready() is False
    assert p.read() is None

def test_slot_oneshot_create_write(agave):
    """Confirm that slot can be created and written from one client
    """
    value = random_string(64)
    p = slots.client.Slot(agave=agave)
    p.create().write(value)
    assert p.name is not None
    assert p.ready() is True
    assert p.read() == value

def test_slot_defer_create_write(agave):
    """Confirm that slot can be written from another client
    """
    value = random_string(64)
    p = slots.client.Slot(agave=agave)
    q = slots.client.Slot(agave=agave)
    slot_name = p.create().name
    # Write using another client
    q.write(value, slot_name)
    assert p.ready() is True
    assert p.read() == value

def test_slot_defer_x2_create_write(agave):
    """Confirm that slot can be written from another client and
    read from yet another client.
    """
    value = random_string(64)

    p = slots.client.Slot(agave=agave)
    q = slots.client.Slot(agave=agave)
    r = slots.client.Slot(agave=agave)
    slot_name = p.create().name
    q.write(value, slot_name)
    assert r.ready(slot_name) is True
    assert r.read(slot_name) == value

def test_slot_delete_after_read(agave):
    """Confirm that slot can be written from another client and
    read from yet another client.
    """
    value = random_string(64)
    p = slots.client.Slot(agave=agave)
    p.create().write(value)
    p_name = p.name
    # p_uuid = p.uuid
    assert p_name is not None
    assert p.ready() is True
    assert p.read(delete=True) == value
    q = slots.client.Slot(agave=agave)
    with pytest.raises(ValueError):
        q.read(key_name=p_name)
