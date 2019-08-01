import os
import json
from datacatalog.linkedstores.association import Association, AssociationError
from datacatalog.linkedstores.annotations import AnnotationError
from datacatalog.linkedstores.annotations.tag import (
    TagAnnotation, TagAnnotationDocument)
from datacatalog.linkedstores.annotations.text import TextAnnotation
from ..schemabase import EventBaseSchema
from ..anno import (DeletedRecordCounts, AssociatedAnnotation)

class TagAnnotationCreateSchema(EventBaseSchema):
    DEFAULT_DOCUMENT_NAME = 'create.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'r'))
        super(TagAnnotationCreateSchema, self).__init__(**j)
        self.update_id()

class Schema(TagAnnotationCreateSchema):
    pass

def get_schema():
    return TagAnnotationCreateSchema()

def action(self, body, token=None):
    # TODO - Allow create-and-link by passing 1+ record UUID?
    self.logger.info('event.create: {}'.format(body))
    return new_tag(self, token=token, **body)

def new_tag(self,
            name=None,
            owner=None,
            description='',
            token=None,
            **kwargs):
    """Creates a new Tag annotation

    Args:
        name (str): Name of the tag
        description (str, optional): Plaintext description of the tag
        owner (str, optional): TACC.cloud username owning the tag

    Returns:
        TagAnnotation: Representation of the new Tag

    Raises:
        AnnotationError: Unable to create the tag
    """

    self.validate_tapis_username(owner, permissive=True)
    anno = self.stores['tag_annotation'].new_tag(name=name,
                                                 description=description,
                                                 owner=owner,
                                                 token=token,
                                                 **kwargs)
    return TagAnnotation(self.sanitize(anno))

def new_tag_annotation(self,
                       connects_to=None,
                       name=None,
                       owner=None,
                       description='',
                       note='',
                       tag_owner=None,
                       token=None, **kwargs):
    """Creates a Tag and associates with Record(s).

    Args:
        connects_to (str): UUID5 of the Record to be annotated
        name (str): Name of the new Tag
        description (str, optional): Plaintext description of the Tag
        note (str, optional): Plaintext rationale for attaching Tag to Record
        owner (str, optional): TACC.cloud username owning the Tag and Association
        tag_owner (str, optional): TACC.cloud username owning the Tag (if different)

    Returns:
        TagAnnotation: Representation of the new Tag

    Raises:
        AnnotationError: Error prevented creation of the Tag Annotation
        AssociationError: Error occurred creating the Association
    """

    if tag_owner is not None:
        self.validate_tapis_username(tag_owner, permissive=True)
    else:
        tag_owner = owner

    connects_from = None
    anno = self.stores['tag_annotation'].new_tag(name=name,
                                                 description=description,
                                                 owner=tag_owner,
                                                 token=token,
                                                 **kwargs)
    connects_from = anno.get('uuid', None)
    assoc = None
    if connects_from is not None:
        assoc = self.stores['association'].associate(
            connects_from, connects_to, note=note, owner=owner)

    return TagAnnotation(self.sanitize(anno))
