import os
import pytest
import sys
import yaml
import json
from . import longrun, delete
from . import data

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog.linkedstores import (annotations, association)

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
def test_tag_annotation_doc(tag_name, tag_desc, tag_owner, tag_valid):
    """Checks iterations of TagAnnotation name and description
    """
    if tag_valid is True:
        doc = annotations.tag.TagAnnotationDocument(
            name=tag_name, description=tag_desc, owner=tag_owner)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = annotations.tag.TagAnnotationDocument(
                name=tag_name, description=tag_desc, owner=tag_owner)
            assert isinstance(doc, dict)

@pytest.mark.parametrize('text_subject,text_body,text_owner,text_child_of,text_valid', [
    (None, 'Body, no subject', 'public', None, True),
    ('Subject, no body', None, 'public', None, False),
    (None, 'Body, no owner', None, None, False),
    (None, 'Body, invalid owner', 'Bevo Longhorn', None, False),
    (None, 'Body, owner email', 'Bevo@sportsball.utexas.edu', None, True), ('bevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevobevo', 'Subject too long', 'public', None, False),
    (None, 'Thread to Association', 'public', '124579ee-9daa-5643-9e71-7801cf481438', False),
    (None, 'Thread to Tag Annotation', 'public', '1221cef4-fab1-538c-837e-7c118c131003', False),
    (None, 'Thread to Text Annotation', 'public', '12345fe3-6c2d-5372-b15a-5547b4f03b5a', True)
])
def test_text_annotation_doc(text_subject, text_body, text_owner, text_child_of, text_valid):
    """Checks iterations of TextAnnotation subject, body, parentage
    """
    opts = dict()
    if text_subject is not None:
        opts['subject'] = text_subject
    if text_body is not None:
        opts['body'] = text_body
    if text_owner is not None:
        opts['owner'] = text_owner
    if text_child_of is not None:
        opts['child_of'] = text_child_of
    if text_valid is True:
        doc = annotations.text.TextAnnotationDocument(**opts)
        assert isinstance(doc, dict)
    else:
        with pytest.raises(Exception):
            doc = annotations.text.TextAnnotationDocument(**opts)
            assert isinstance(doc, dict)
