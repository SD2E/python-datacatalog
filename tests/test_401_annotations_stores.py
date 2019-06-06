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

@pytest.mark.parametrize('text_subject,text_body,text_owner,text_child_of,text_valid', [
    ('Test', 'Message for test_new_reply()', 'public', None, True),
    (None, 'Body, no subject', 'public', None, True),
    ('Subject, no body', None, 'public', None, False),
    (None, 'Body, no owner', None, None, False),
    (None, 'Body, invalid owner', 'Bevo Longhorn', None, False),
    (None, 'Body, owner email', 'Bevo@sportsball.utexas.edu', None, True), ('bevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevo', 'Subject too long', 'public', None, False)
])
def test_new_text(mongodb_settings, text_subject, text_body,
                  text_owner, text_child_of, text_valid):
    """Checks iterations of TextAnnotation subject, body, parentage
    """
    store = annotations.text.TextAnnotationStore(mongodb_settings)
    opts = dict()
    args = list()
    if text_body is not None:
        args.append(text_body)
    if text_subject is not None:
        opts['subject'] = text_subject
    if text_owner is not None:
        opts['owner'] = text_owner
    # if text_child_of is not None:
    #     opts['child_of'] = text_child_of
    if text_valid is True:
        doc = store.new_text(*args, **opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = store.new_text(*args, **opts)
            assert isinstance(doc, dict)

@pytest.mark.parametrize('text_subject,text_body,text_owner,text_child_of,text_valid', [
    (None, 'Cannot reply to Association', 'public', '124579ee-9daa-5643-9e71-7801cf481438', False),
    (None, 'Cannot reply to Tag Annotation', 'public', '1221cef4-fab1-538c-837e-7c118c131003', False),
    (None, 'Can reply to Text Annotation', 'public', '123a664f-5f11-5c42-a2b4-de37ea04756a', True),
    (None, 'Can reply to a reply', 'public', '1233b4cd-23cc-5db1-9041-b4405479eb99', True),
    (None, 'Cannot reply to non-existent Text Anno', 'public', '123db150-cb9f-5201-9dc5-3de4f7437d58', False)
])
def test_new_reply(mongodb_settings, text_subject, text_body,
                   text_owner, text_child_of, text_valid):
    """Checks iterations of TextAnnotation subject, body, parentage
    """
    store = annotations.text.TextAnnotationStore(mongodb_settings)
    opts = dict()
    args = list()
    if text_child_of is not None:
        args.append(text_child_of)
    if text_body is not None:
        args.append(text_body)
    if text_subject is not None:
        opts['subject'] = text_subject
    if text_owner is not None:
        opts['owner'] = text_owner
    if text_valid is True:
        doc = store.new_reply(*args, **opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = store.new_reply(*args, **opts)
            assert isinstance(doc, dict)

@pytest.mark.parametrize('tag_name,tag_desc,tag_owner,tag_valid', [
    ('mi', 'Too short', 'public', False),
    ('doe', 'Minimum length', 'public', True),
    ('peep123', 'Valid tag', 'public', True),
    ('123peep', 'Can start with number', 'public', True),
    ('.123peep', 'Cannot start with delim', 'public', False),
    ('peep peep', 'Space disallowed', 'public', False),
    ('meep_meep', 'Underscore disallowed', 'public', False),
    ('meepmeepmeepmeepmeepmeepmeepmeepmeepmeepmeepmeepmeepmeepmeepmeepmeep', 'Tag too long', 'public', False),
    ('do-re-mi', 'Doe, a deer, a female deer; (Re!) ray, a drop of golden sun; (Mi!) me, a name I call myself; (Fa!) far, a long, long way to run; (So!) sew, a needle pulling thread; (La!) la, a note to follow so; (Ti!) tea, a drink with jam and bread; That will bring us back to do oh oh oh.', 'public', False),
    ('do-re-mi', 'Doe, a deer, a female deer; (Re!) ray, a drop of golden sun; (Mi!) me, a name I call myself; (Fa!) far, a long, long way to run; (So!) sew, a needle pulling thread; (La!) la, a note to follow so; (Ti!) tea, a drink with jam and bread', 'public', True)
])
def test_new_tag(mongodb_settings, tag_name, tag_desc, tag_owner, tag_valid):
    """Checks iterations of TagAnnotation name, description, owner
    """
    store = annotations.tag.TagAnnotationStore(mongodb_settings)
    opts = dict()
    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if tag_owner is not None:
        opts['owner'] = tag_owner

    if tag_valid is True:
        doc = store.new_tag(**opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = store.new_tag(**opts)
            assert isinstance(doc, dict)
