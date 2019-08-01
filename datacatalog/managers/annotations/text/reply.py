import os
import json
from datacatalog.linkedstores.association import Association, AssociationError
from datacatalog.linkedstores.annotations import AnnotationError
from datacatalog.linkedstores.annotations.text import (
    TextAnnotation, TextAnnotationDocument)
from ..schemabase import EventBaseSchema
from ..anno import (DeletedRecordCounts, AssociatedAnnotation)

# TODO - Allow association of a Text with >1 Records?

class TextAnnotationReplySchema(EventBaseSchema):
    DEFAULT_DOCUMENT_NAME = 'reply.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'r'))
        super(TextAnnotationReplySchema, self).__init__(**j)
        self.update_id()

class Schema(TextAnnotationReplySchema):
    pass

def get_schema():
    return TextAnnotationReplySchema()

def action(self, body, token=None):
    self.logger.info('event.reply: {}'.format(body))
    return new_reply(self, token=token, **body)

def new_reply(self,
              reply_to=None,
              subject=None,
              body=None,
              owner=None,
              token=None,
              **kwargs):
    """Reply to a Text note

    Args:
        reply_to (str): UUID of the Text Annotation being replied to
        subject (str): Subject for the Reply (Default: Re: Parent subject)
        body (str, optional): Body of the Reply (Max size: 2 kb)
        owner (str, optional): TACC.cloud username or email owner for the Reply

    Returns:
        TextAnnotation: Representation of the Reply

    Raises:
        AnnotationError: Error prevented creation of the Reply
    """
    self.validate_tapis_username(owner)

    if isinstance(reply_to, str):
        self.validate_uuid(reply_to)
    elif isinstance(reply_to, list):
        for u in reply_to:
            self.validate(u)

    text_anno_rec = self.get_by_uuid(reply_to, permissive=False)
    # Thread the subject line, just like email 💌
    if subject is None:
        orig_subject = text_anno_rec.get('subject', '')
        if orig_subject is not None:
            subject = 'Re: ' + orig_subject

    # assoc_uuid = None
    anno = self.stores['text_annotation'].new_reply(
        reply_to, subject=subject, body=body,
        owner=owner, token=token)
    return TextAnnotation(self.sanitize(anno))
