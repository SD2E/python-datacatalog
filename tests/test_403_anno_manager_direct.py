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

@pytest.mark.parametrize('target_uuid,text_body,text_subject,text_owner,test_pass', [
    ('1012da8b-663a-591f-a13d-cdf5277656a0', 'This is very challenging!', 'My opinion on Pipeline Automation', 'public', True),
    # CP does not exist
    ('101f3911-c654-5087-8fcd-bc338cec6496', 'This cannot be very challenging', 'I agree', 'public', False)
])
def test_new_text_anno(mongodb_settings, agave, target_uuid,
                       text_body, text_subject, text_owner, test_pass):
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    opts = dict()

    if target_uuid is not None:
        opts['connects_to'] = target_uuid
    if text_subject is not None:
        opts['subject'] = text_subject
    if text_body is not None:
        opts['body'] = text_body
    if text_owner is not None:
        opts['owner'] = text_owner

    if test_pass is True:
        doc = annotations.text.create.new_text(mgr, **opts)
#        doc = mgr.new_text_annotation(*args, **opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = annotations.text.create.new_text(mgr, **opts)
            assert isinstance(doc, dict)

@pytest.mark.parametrize('reply_to,text_body,text_subject,text_owner,test_pass', [
    ('1235b738-4689-51d1-a6db-6576010ee451', 'I do not understand why', None, 'world', True),
    ('123a5390-be15-567d-8d65-70ee56bb0b66', 'Cannot follow up since target does not exist', None, 'public', False),
    ('1234b02a-f40d-51bc-8f34-9bc8539dcd16', 'See this reference [1]', None, 'world', True),
])
def test_reply_text_anno(mongodb_settings, agave, reply_to,
                         text_body, text_subject, text_owner, test_pass):
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    opts = dict()

    if reply_to is not None:
        opts['reply_to'] = reply_to
    if text_subject is not None:
        opts['subject'] = text_subject
    if text_body is not None:
        opts['body'] = text_body
    if text_owner is not None:
        opts['owner'] = text_owner

    if test_pass is True:
        doc = annotations.text.reply.new_reply(mgr, **opts)
#        doc = mgr.new_text_annotation(*args, **opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = annotations.text.reply.new_reply(mgr, **opts)
            assert isinstance(doc, dict)

@pytest.mark.skip(reason="currently not implemented")
@pytest.mark.parametrize('target_uuid,tag_name,tag_desc,tag_owner,assoc_owner,tag_valid', [
    ('1012da8b-663a-591f-a13d-cdf5277656a0', 'much.challenge-problem', None, 'world', 'vaughn', True),
    ('1144f727-8827-5126-8e03-f35e8cb6f070', 'so.experimental-design', None, 'world', 'jfonner', True),
    ('102e95e6-67a8-5a06-9484-3131c6907890', 'experiment.wow', None, 'world', 'maytal', True),
    ('102e95e6-67a8-5a06-9484-3131c6907890', 'experiment_underscore.wow', None, 'world', 'maytal', False)
])
def test_new_tag_anno(mongodb_settings, agave, target_uuid, tag_name,
                      tag_desc, tag_owner, assoc_owner, tag_valid):
    """Checks iterations of TagAnnotation name and description
    """
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    opts = dict()

    if target_uuid is not None:
        opts['connects_to'] = target_uuid
    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if tag_owner is not None:
        opts['tag_owner'] = tag_owner
    if assoc_owner is not None:
        opts['owner'] = assoc_owner

    if tag_valid is True:
        doc = mgr.new_tag_annotation(*args, **opts)
        assert isinstance(doc, annotations.AnnotationResponse)
    else:
        with pytest.raises(Exception):
            doc = mgr.new_tag_annotation(*args, **opts)
            assert isinstance(doc, dict)

@pytest.mark.skip(reason="currently not implemented")
@pytest.mark.parametrize('target_uuid,tag_valid', [
    ('12236906-bfee-56cd-bbc2-616f9a32cd43', True)
])
def test_publish_tag(mongodb_settings, agave, target_uuid, tag_valid):
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    if tag_valid is True:
        doc = mgr.publish_tag(target_uuid)
        assert doc['owner'] == annotations.AnnotationManager.PUBLIC_USER
    else:
        with pytest.raises(Exception):
            doc = mgr.publish_tag(target_uuid)
            assert doc['owner'] == annotations.AnnotationManager.PUBLIC_USER

@pytest.mark.skip(reason="currently not implemented")
@pytest.mark.parametrize('target_uuid,tag_valid', [
    ('12234e7a-68ec-5547-b111-f29e18a75aa2', True)
])
def test_unpublish_tag(mongodb_settings, agave, target_uuid, tag_valid):
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    if tag_valid is True:
        doc = mgr.unpublish_tag(target_uuid)
        assert doc[1] is True
    else:
        with pytest.raises(Exception):
            doc = mgr.unpublish_tag(target_uuid)
            assert doc[1] is True

@pytest.mark.skip(reason="currently not implemented")
@pytest.mark.parametrize('target_uuid,tag_name,tag_desc,tag_owner,assoc_owner,test_pass', [
    ('1012da8b-663a-591f-a13d-cdf5277656a0', 'much.challenge-problem', None, 'world', 'vaughn', True),
    ('1144f727-8827-5126-8e03-f35e8cb6f070', 'so.experimental-design', None, 'world', 'jfonner', True),
    ('102e95e6-67a8-5a06-9484-3131c6907890', 'experiment.wow', None, 'world', 'maytal', True)
])
def test_amgr_delete_tag(mongodb_settings, agave, target_uuid, tag_name, tag_desc, tag_owner, assoc_owner,test_pass):
    mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    opts = dict()

    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if assoc_owner is not None:
        opts['owner'] = assoc_owner

    if test_pass is True:
        doc = annotations.tag.delete.delete_tag(mgr, **opts)
#        doc = mgr.new_text_annotation(*args, **opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = annotations.text.reply.new_reply(mgr, **opts)
            assert isinstance(doc, dict)

