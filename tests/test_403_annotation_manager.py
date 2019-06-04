import os
import pytest
import sys
import yaml
import json
from .fixtures.mongodb import mongodb_settings
from .fixtures.agave import agave, credentials
from . import longrun, delete
from . import data

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog.managers import annotations

@pytest.mark.parametrize('target_uuid,text_body,text_subject,text_owner,text_valid', [
    ('1012da8b-663a-591f-a13d-cdf5277656a0', 'This is very challenging!', 'My opinion on Pipeline Automation', 'public', True),
    ('101f3911-c654-5087-8fcd-bc338cec6496', 'This cannot be very challenging', 'I agree', 'public', False)
])
def test_new_text_anno(mongodb_settings, agave, target_uuid,
                       text_body, text_subject, text_owner, text_valid):
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    opts = dict()
    args = list()

    if target_uuid is not None:
        args.append(target_uuid)
    if text_body is not None:
        args.append(text_body)
    if text_subject is not None:
        opts['subject'] = text_subject
    if text_owner is not None:
        opts['owner'] = text_owner

    # raise SystemExit(opts)

    if text_valid is True:
        doc = mgr.new_text_annotation(*args, **opts)
        assert isinstance(doc, annotations.AnnotationResponse)
    else:
        with pytest.raises(Exception):
            doc = mgr.new_text_annotation(*args, **opts)
            assert isinstance(doc, annotations.AnnotationResponse)

@pytest.mark.parametrize('target_uuid,text_body,text_subject,text_owner,text_valid', [
    ('1235b738-4689-51d1-a6db-6576010ee451', 'I do not understand why', None, 'world', True),
    ('123a5390-be15-567d-8d65-70ee56bb0b66', 'Cannot follow up since target does not exist', None, 'public', False),
    ('1234b02a-f40d-51bc-8f34-9bc8539dcd16', 'See this reference [1]', None, 'world', True),
])
def test_reply_text_anno(mongodb_settings, agave, target_uuid,
                         text_body, text_subject, text_owner, text_valid):
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    opts = dict()
    args = list()

    if target_uuid is not None:
        args.append(target_uuid)
    if text_body is not None:
        opts['body'] = text_body
    if text_subject is not None:
        opts['subject'] = text_subject
    if text_owner is not None:
        opts['owner'] = text_owner

    if text_valid is True:
        doc = mgr.reply_text_annotation(*args, **opts)
        assert isinstance(doc, annotations.AnnotationResponse)
    else:
        with pytest.raises(Exception):
            doc = mgr.reply_text_annotation(*args, **opts)
            assert isinstance(doc, annotations.AnnotationResponse)
