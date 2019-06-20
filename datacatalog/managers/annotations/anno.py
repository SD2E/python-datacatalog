import collections
from ..common import Manager
from copy import deepcopy
from pymongo.cursor import Cursor
from datacatalog.identifiers import typeduuid
from datacatalog.linkedstores.association import Association, AssociationError
from datacatalog.linkedstores.annotations import AnnotationError
from datacatalog.linkedstores.annotations.tag import (
    TagAnnotation, TagAnnotationDocument)
from datacatalog.linkedstores.annotations.text import TextAnnotation

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
        anno = self.stores['text_annotation'].new_text(
            body=body, subject=subject, owner=owner, token=token)
        anno_uuid = anno.get('uuid', None)
        if anno_uuid is not None:
            self.stores['association'].associate(
                anno_uuid, record_uuid, owner=owner)
        else:
            raise AssociationError(
                'Failed to associate record and annotation')
        return TextAnnotation(self.sanitize(anno))

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
        return TextAnnotation(self.sanitize(anno))

    def delete_text_annotation(self, text_anno_uuid, token=None, **kwargs):
        # Need to think about how to handle this since it may involve recursion
        pass

    def prune_text_annotations(self, record_uuid, token=None, **kwargs):
        # Need to think about how to handle this since it may involve recursion
        pass

    def new_tag(self,
                name=None,
                owner=None,
                description='',
                token=None, **kwargs):
        """Creates a new Tag

        Args:
            name (str): Name of the tag
            description (str, optional): Plaintext description of the tag
            owner (str): TACC.cloud username owning the tag

        Returns:
            dict: Representation of the tag

        Raises:
            AnnotationError: Unable to create the tag
        """

        self.validate_tapis_username(owner)
        anno = self.stores['tag_annotation'].new_tag(name=name,
                                                     description=description,
                                                     owner=owner,
                                                     token=token,
                                                     **kwargs)
        return TagAnnotation(self.sanitize(anno))

    def new_tag_association(self, uuid, record_uuid,
                            owner=None,
                            token=None, **kwargs):
        """Associates a Tag with 1+ other metadata records
        """
        if typeduuid.get_uuidtype(uuid) != 'tag_annotation':
            raise ValueError('Function only accepts tag UUIDs')
        return self._new_annotation_association(
            uuid, record_uuid,
            owner=owner, token=token, **kwargs)

    def new_text_association(self, uuid, record_uuid,
                             owner=None,
                             token=None, **kwargs):
        """Associates a Text Annotation with 1+ other metadata records
        """
        if typeduuid.get_uuidtype(uuid) != 'text_annotation':
            raise ValueError('Function only accepts tag UUIDs')
        return self._new_annotation_association(
            uuid, record_uuid,
            owner=owner, token=token, **kwargs)

    def _new_annotation_association(self, uuid, record_uuid,
                                    owner=None, token=None, **kwargs):
        self.validate_tapis_username(owner)
        associations = list()

        # Either a single or list of target UUIDs is allowed. A list of
        # ssociations is returned in either case. This allows batch association
        # of a tag to multiple UUIDs
        if isinstance(record_uuid, str):
            record_uuids = [record_uuid]
        elif isinstance(record_uuid, list):
            record_uuids = record_uuid
        else:
            raise ValueError('"record_uuid" must be a single or list of UUIDs')

        # TODO - Consider parallelizing this
        for ruuid in record_uuids:
            try:
                assoc = self.stores['association'].associate(
                    uuid, ruuid, owner=owner)
                associations.append(Association(self.sanitize(assoc)))
            except Exception as exc:
                self.logger.error('Association not created: {}'.format(exc))
        return associations

    def tags_list(self, limit=None, skip=None,
                  public=False, visible=True):
        """Retrieve the known list of Tags

        Args:
            limit (int, optional): Maximum number of records to return
            skip (int, optional): Skip this many matching records
            public (bool, optional): Return only publis tags
            visible (bool, optional): Return only tags that are not soft-deleted

        Returns:
            list: List of dict objects representing each tag
        """
        tags_all = list()
        query = dict()
        if visible:
            query[self.DELETE_FIELD] = True
        if public is True:
            query['owner'] = self.PUBLIC_USER
        for t in self.stores['tag_annotation'].query(
                query, attr_dict=True, projection=None, limit=limit, skip=skip):
            tags_all.append(t)
        return tags_all

    def new_tag_annotation(self, record_uuid,
                           name=None,
                           owner=None,
                           description='',
                           tag_owner=None,
                           token=None, **kwargs):
        """Creates a new Tag in user namespace and associates it with a
           specified metadata record.

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

    def publish_tag(self, uuid,
                    clone_associations=True,
                    remove_original=False,
                    token=None):
        """Copy a Tag into the public namespace

        Args:
            tag_uuid (str): UUID5 of the tag to publish

        Returns:
            dict: Representation of the newly public tag
        """
        anno = self.stores['tag_annotation'].find_one_by_uuid(uuid)
        if anno is None:
            raise ValueError(
                'Tag with UUID {} does not exist'.format(uuid))
        if anno.get('owner', None) == self.PUBLIC_USER:
            return anno

        self.logger.info('Cloning tag {}'.format(uuid))
        new_anno = TagAnnotationDocument(
            name=anno['name'],
            description=anno['description'],
            owner=self.PUBLIC_USER)
        # Impdepotent clone
        resp = self.stores['tag_annotation'].add_update_document(
            new_anno, token=None)
        resp_2 = self.stores['tag_annotation'].undelete(
            resp['uuid'], token=token)
        cloned_uuid = resp_2.get('uuid')

        if clone_associations:
            # Clone associations (filtering by visible)
            self.logger.info('Finding associations for tag {}'.format(uuid))
            query = {'connects_from': uuid, self.DELETE_FIELD: True}
            proj = {'connects_to': 1}
            orig_assoc = self.stores['association'].query(
                query=query, projection=proj)
            cloned_assoc_uuids = list()
            if isinstance(orig_assoc, Cursor):
                for a in orig_assoc:
                    cloned_assoc_uuids.extend(a.get('connects_to', []))

            cloned_assoc_uuids = list(set(cloned_assoc_uuids))
            cloned_assoc_uuids.sort()

            self.logger.info(
                'Cloning {} associations for tag {}'.format(
                    len(cloned_assoc_uuids), uuid))
            self.new_tag_association(
                cloned_uuid, cloned_assoc_uuids, owner=self.PUBLIC_USER)

        # We do not return any details on the associations,
        # only the cloned tag
        return TagAnnotation(self.sanitize(resp_2))

    def unpublish_tag(self, tag_uuid, token=None):
        """Remove a Tag from the public namespace

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

        # TODO - Delete associations referring to cloned tag
        return TagAnnotation(self.sanitize(resp))

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
