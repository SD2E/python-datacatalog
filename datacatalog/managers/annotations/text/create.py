import os
import json
from datacatalog.linkedstores.association import Association, AssociationError
from datacatalog.linkedstores.annotations import AnnotationError
from datacatalog.linkedstores.annotations.text import (
    TextAnnotation, TextAnnotationDocument)
from ..schemabase import EventBaseSchema
from ..anno import (DeletedRecordCounts, AssociatedAnnotation)

# TODO - Allow association of a Text with >1 Records?

class TextAnnotationCreateSchema(EventBaseSchema):
    DEFAULT_DOCUMENT_NAME = 'create.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'r'))
        super(TextAnnotationCreateSchema, self).__init__(**j)
        self.update_id()

class Schema(TextAnnotationCreateSchema):
    pass

def get_schema():
    return TextAnnotationCreateSchema()

def action(self, body, token=None):
    self.logger.info('event.create: {}'.format(body))
    return new_text(self, token=token, **body)

def new_text(self,
             connects_to=None,
             subject=None,
             body=None,
             owner=None,
             token=None,
             **kwargs):
    """Creates a Text Note on one or more Data Catalog Records

    Args:
        connects_to (str/list): UUID of the target Record(s)
        subject (str): Subject of the Text Annotation
        body (str, optional): Body of the Text Annotation (Max size: 2 kb)
        owner (str, optional): TACC.cloud username or email owner for the Text Annotation

    Returns:
        TextAnnotation: Representation of the new Text

    Raises:
        AnnotationError: Error prevented creation of the Text Annotation
        AssociationError: Error occurred linking to a Record
    """
    self.validate_tapis_username(owner, permissive=True)
    if isinstance(connects_to, str):
        self.validate_uuid(connects_to)
    elif isinstance(connects_to, list):
        for u in connects_to:
            self.validate(u)
    # if body is None or body == '':
    #     raise ValueError('"body" cannot be empty or null')
    anno = self.stores['text_annotation'].new_text(
        body=body, subject=subject, owner=owner, token=token)
    anno_uuid = anno.get('uuid', None)
    if anno_uuid is not None:
        self.stores['association'].associate(
            anno_uuid, connects_to, owner=owner)
    else:
        raise AssociationError(
            'Failed to associate record and annotation')
    return TextAnnotation(self.sanitize(anno))
