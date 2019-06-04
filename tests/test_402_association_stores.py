import os
import pytest
import sys
import yaml
import json
from .fixtures.mongodb import mongodb_settings
from . import longrun, delete
from . import data

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog.linkedstores import (annotations, association)

@pytest.mark.parametrize('anno_uuid,rec_uuid,assoc_owner,assoc_valid', [
    # can tag an experiment design
    ('1221cef4-fab1-538c-837e-7c118c131003', '1144f727-8827-5126-8e03-f35e8cb6f070', 'public', True),
    # cannot tag another tag
    ('1221cef4-fab1-538c-837e-7c118c131003', '122a70d8-a52e-56a2-8444-a968aea16e1c', 'public', False),
    # cannot tag a text annotation
    ('1221cef4-fab1-538c-837e-7c118c131003', '12345fe3-6c2d-5372-b15a-5547b4f03b5a', 'public', False),
    # can free-text an experiment design
    ('12345fe3-6c2d-5372-b15a-5547b4f03b5a', '1144f727-8827-5126-8e03-f35e8cb6f070', 'public', True),
    # can tag a pipeline
    ('122f45db-46dc-5e5c-a12e-3ec37afed7f8', '106c46ff-8186-5756-a934-071f4497b58d', 'public', True)
])
def test_associate(mongodb_settings, anno_uuid, rec_uuid,
                   assoc_owner, assoc_valid):
    store = association.AssociationStore(mongodb_settings)
    opts = dict()
    args = list()
    if anno_uuid is not None:
        args.append(anno_uuid)
    if rec_uuid is not None:
        args.append(rec_uuid)
    if assoc_owner is not None:
        opts['owner'] = assoc_owner

    # if text_child_of is not None:
    #     opts['child_of'] = text_child_of
    if assoc_valid is True:
        doc = store.associate(*args, **opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = store.associate(*args, **opts)
            assert isinstance(doc, dict)

@pytest.mark.parametrize('anno_uuid,rec_uuid,assoc_owner,dissoc_valid', [
    # can untag an experiment design
    ('1221cef4-fab1-538c-837e-7c118c131003', '1144f727-8827-5126-8e03-f35e8cb6f070', 'public', True),
    # can un-text an experiment design
    ('12345fe3-6c2d-5372-b15a-5547b4f03b5a', '1144f727-8827-5126-8e03-f35e8cb6f070', 'public', True),
    # can un-tag a pipeline
    ('122f45db-46dc-5e5c-a12e-3ec37afed7f8', '106c46ff-8186-5756-a934-071f4497b58d', 'public', True),
    # cannot dissociate if assoc does not exist
    ('122f45db-46dc-5e5c-a12e-3ec37afed7f8', '114d5f28-8bb7-5d44-9df9-e75a5223308d', 'public', False),
    ('122f45db-46dc-5e5c-a12e-3ec37afed7f8', '122ab293-010d-5831-a89c-f9059850f148', 'public', False),
    ('1236bca1-5d0b-5797-8cb7-6c97015ef1fe', '106c46ff-8186-5756-a934-071f4497b58d', 'public', False)

])
def test_dissociate(mongodb_settings, anno_uuid, rec_uuid,
                    assoc_owner, dissoc_valid):
    store = association.AssociationStore(mongodb_settings)
    opts = dict()
    args = list()
    if anno_uuid is not None:
        args.append(anno_uuid)
    if rec_uuid is not None:
        args.append(rec_uuid)
    if assoc_owner is not None:
        opts['owner'] = assoc_owner

    if dissoc_valid is True:
        doc = store.dissociate(*args, **opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = store.dissociate(*args, **opts)
            assert isinstance(doc, dict)
