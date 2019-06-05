import collections
from ..common import Manager
from copy import deepcopy
from datacatalog.linkedstores.association import AssociationError
from datacatalog.linkedstores.annotations import AnnotationError
from datacatalog.linkedstores.annotations.tag import TagAnnotationDocument

from datacatalog import settings

AnnotationResponse = collections.namedtuple(
    'AnnotationResponse', 'record_uuid annotation_uuid association_uuid')

class AnnotationManager(Manager):

    PUBLIC_USER = settings.TAPIS_ANY_AUTHENTICATED_USERNAME

    def __init__(self, mongodb, agave=None, *args, **kwargs):
        Manager.__init__(self, mongodb, agave=agave, *args, **kwargs)

    def new_text_annotation(self, record_uuid, body=None, owner=None,
                            subject=None, token=None, **kwargs):
        """Creates a new Text Annotation annotating a specific record

        Args:
            record_uuid (str): UUID5 of record to be annotated
            body (str): Body of the annotation message (2 kb)
            owner (str): TACC.cloud username or email owner for the message
            subject (str, optional): Subject of the annotation message

        Returns:
            AnnotationResponse: A named tuple containing relevant UUIDs

        Raises:
            AnnotationError: Error prevented creation of the Text Annotation
            AssociationError: Error occurred creating the final linkage
        """
        self.validate_tapis_username(owner)
        self.validate_uuid(record_uuid)
        assoc_uuid = None
        anno = self.stores['text_annotation'].new_text(
            body=body, subject=subject, owner=owner, token=token)
        anno_uuid = anno.get('uuid', None)
        if anno_uuid is not None:
            assoc = self.stores['association'].associate(
                anno_uuid, record_uuid, owner=owner)
            assoc_uuid = assoc.get('uuid', None)
        else:
            raise AssociationError(
                'Failed to associate record and annotation')

        a = AnnotationResponse(annotation_uuid=anno_uuid,
                               association_uuid=assoc_uuid,
                               record_uuid=record_uuid)
        return a

    def reply_text_annotation(self, text_anno_uuid, body=None, owner=None,
                              subject=None, token=None, **kwargs):
        """Creates a new Text Annotation that replies to another one

        Args:
            text_anno_uuid (str): UUID5 for the text record being responded to
            body (str): Body of the annotation message (2 kb)
            owner (str): TACC.cloud username or email owner for the message
            subject (str, optional): Subject of the annotation message

        Returns:
            AnnotationResponse: A named tuple containing relevant UUIDs

        Raises:
            AnnotationError: Error prevented creation of the Text Annotation
            AssociationError: Error occurred creating the association
        """
        self.validate_tapis_username(owner)
        text_anno_rec = self.get_by_uuid(text_anno_uuid, permissive=False)
        # Thread the subject line, just like email 💌
        if subject is None:
            orig_subject = text_anno_rec.get('subject', '')
            if orig_subject is not None:
                subject = 'Re: ' + orig_subject

        # assoc_uuid = None
        anno = self.stores['text_annotation'].new_reply(
            text_anno_uuid, subject=subject, body=body,
            owner=owner, token=token)
        anno_uuid = anno.get('uuid', None)
        # If we ever decide to create an association even for threaded
        # text annotation docs, we would do it here
        a = AnnotationResponse(annotation_uuid=anno_uuid,
                               association_uuid=None,
                               record_uuid=text_anno_uuid)
        return a

    def delete_text_annotation(self, text_anno_uuid, token=None, **kwargs):
        # Need to think about how to handle this since it may involve recursion
        pass

    def prune_text_annotations(self, record_uuid, token=None, **kwargs):
        # Need to think about how to handle this since it may involve recursion
        pass

    def new_tag_annotation(self, record_uuid,
                           name=None,
                           owner=None,
                           description='',
                           tag_owner=None,
                           token=None, **kwargs):
        """Creates a new Tag Annotation annotating a specific record

        Args:
            record_uuid (str): UUID5 of record to be annotated
            name (str): Name of the tag
            description (str, optional): Plaintext description of the tag
            owner (str): TACC.cloud username owning the tag and association
            tag_owner (str, optional): TACC.cloud username owning the tag (if different)

        Returns:
            AnnotationResponse: A named tuple containing relevant UUIDs

        Raises:
            AnnotationError: Error prevented creation of the Tag Annotation
            AssociationError: Error occurred creating the association
        """

        self.validate_tapis_username(owner)
        if tag_owner is not None:
            self.validate_tapis_username(tag_owner)
        else:
            tag_owner = owner

        assoc_uuid = None
        anno = self.stores['tag_annotation'].new_tag(name=name,
                                                     description=description,
                                                     owner=tag_owner,
                                                     token=token, **kwargs)
        anno_uuid = anno.get('uuid', None)
        if anno_uuid is not None:
            assoc = self.stores['association'].associate(
                anno_uuid, record_uuid, owner=owner)
            assoc_uuid = assoc.get('uuid', None)

        a = AnnotationResponse(annotation_uuid=anno_uuid,
                               association_uuid=assoc_uuid,
                               record_uuid=record_uuid)
        return a

    def publish_tag_annotation(self, tag_uuid,
                               remove_original=False, token=None):
        """Copy a tag into the public namespace

        Args:
            tag_uuid (str): UUID5 of the tag to publish

        Returns:
            dict: Representation of the newly public tag
        """
        anno = self.stores['tag_annotation'].find_one_by_uuid(tag_uuid)
        if anno is None:
            raise ValueError(
                'Tag with UUID {} does not exist'.format(tag_uuid))
        if anno.get('owner', None) == self.PUBLIC_USER:
            return anno

        new_anno = TagAnnotationDocument(
            name=anno['name'],
            description=anno['description'],
            owner=self.PUBLIC_USER)

        resp = self.stores['tag_annotation'].add_update_document(
            new_anno, token=None)
        return self.stores['tag_annotation'].undelete(
            resp['uuid'], token=token)

    def unpublish_tag_annotation(self, tag_uuid, token=None):
        """Remove a tag from the public namespace

        Args:
            tag_uuid (str): UUID5 of the tag to publish

        Returns:
            dict: Representation of the unpublished tag
        """
        anno = self.stores['tag_annotation'].find_one_by_uuid(tag_uuid)
        if anno is None:
            raise ValueError(
                'Tag with UUID {} does not exist'.format(tag_uuid))
        if anno.get('owner', None) != self.PUBLIC_USER:
            raise ValueError('Only public tags can be unpublished')

        resp = self.stores['tag_annotation'].delete_document(
            tag_uuid, token=None)
        return resp

    def prune_tag_annotations(self, record_uuid, token=None, **kwargs):
        pass

    def prune_orphan_annotations(self, record_uuid, token=None, **kwargs):
        self.prune_text_annotations(record_uuid, token=token, **kwargs)
        self.prune_tag_annotations(record_uuid, token=token, **kwargs)
        return True

# Create a Text Anno AND bind to record in one shot
# Create a Text Anno AND bind as child of another in one shot
# Validate usernames via Agave call
# Create and retire Tag and Text associations
# Batch purge by target, source, username
