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

    def _new_annotation_association(self, anno_uuid,
                                    record_uuid,
                                    owner=None,
                                    note='',
                                    token=None,
                                    **kwargs):
        """Private: Creates an Association between a Record and an Annotation.
        """
        self.validate_tapis_username(owner)
        # Either a single or list of target UUIDs is allowed. A list of
        # associations is returned in either case. This promotes batch
        # association of an Annotation to multiple UUIDs

        record_uuids = self.listify_uuid(record_uuid)
        associations = list()

        # TODO - Consider parallelizing this
        for record_uuid in record_uuids:
            try:
                self.logger.debug('Associating anno:{} with record: {}'.format(anno_uuid, record_uuid))
                assoc = self.stores['association'].associate(
                    anno_uuid, record_uuid, note=note, owner=owner)
                associations.append(Association(self.sanitize(assoc)))
            except Exception as exc:
                self.logger.error('Association not created: {}'.format(exc))

        if len(associations) != len(record_uuids):
            self.logger.warning('Different number of records requested as linked')

        return associations

    def _associations_for_annotation(self,
                                     connects_from,
                                     connects_to=None,
                                     owner=None,
                                     only_visible=True):
        """Private: Finds Associations referencing an Annotation

        Arguments:
            connects_from (str): UUID of the Annotation to query
            connects_to (str/list, optional): Record UUID(s) to filter the response on
            only_visible (bool, optional): Return items not marked as deleted

        Returns:
            list: Associations connected with the specified Annotation
        """
        self.logger.info(
            'Finding associations for annotation {}'.format(connects_from))

        query = {'connects_from': connects_from}
        if connects_to is not None:
            query['connects_to'] = connects_to

        if only_visible:
            query[self.stores['association'].DELETE_FIELD] = True
        # TODO - revisit public/userspace filtering - do we want to return public & username or just username
        if owner is not None:
            query['owner'] = owner

        orig_assoc = self.stores['association'].query(
            query=query)
        found_associations = list()
        if isinstance(orig_assoc, Cursor):
            for a in orig_assoc:
                # # When filter_field is 'uuid', the response is a single str
                # # but is a list of str otherwise, so pass thru listify_uuid
                # # to be safe
                # if isinstance(fa, str):
                #     fa = self.listify_uuid(fa)
                # Uniqueness filter. Do not use list(set()) on strings
                if a not in found_associations:
                    found_associations.append(a)
        self.logger.debug(
            'Found {} associations from {}'.format(
                len(found_associations), connects_from))

        return found_associations

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

        self.validate_tapis_username(owner)
        anno = self.stores['tag_annotation'].new_tag(name=name,
                                                     description=description,
                                                     owner=owner,
                                                     token=token,
                                                     **kwargs)
        return TagAnnotation(self.sanitize(anno))

    def tags_list(self,
                  limit=None,
                  skip=None,
                  public=True,
                  private=True,
                  visible=True,
                  **kwargs):
        """Retrieves the list of Tags

        Args:
            limit (int, optional): Maximum number of records to return
            skip (int, optional): Skip this many matching records
            public (bool, optional): Return public tags
            private (bool, optional): Return private (to user) tags
            visible (bool, optional): Return only tags that are not soft-deleted

        Returns:
            tuple: All tags matching the filter criteria
        """
        tags_all = list()
        query = dict()
        if visible:
            query[self.stores['association'].DELETE_FIELD] = True
        if public is True:
            query['owner'] = self.PUBLIC_USER
        for t in self.stores['tag_annotation'].query(
                query, attr_dict=True, projection=None, limit=limit, skip=skip):
            tags_all.append(t)
        return tuple(tags_all)

    def new_tag_association(self,
                            connects_from=None,
                            connects_to=None,
                            owner=None,
                            token=None,
                            **kwargs):
        """Associates a Tag with one or more Data Catalog records.

        Args:
            connects_from (str): UIUD of the Tag (connects_from)
            connects_to (str/list): UUID (or list) of Records to connect with
            owner (str, optional): TACC.cloud username owning the association

        Returns:
            tuple: The newly created (or updated) Association
        """
        if typeduuid.get_uuidtype(connects_from) != 'tag_annotation':
            raise ValueError('Function only accepts tag UUIDs')
        assoc = self._new_annotation_association(
            connects_from, connects_to,
            owner=owner, token=token, **kwargs)
        return tuple(assoc)

    def new_tag_annotation(self,
                           connects_to=None,
                           name=None,
                           owner=None,
                           description='',
                           tag_owner=None,
                           association_note='',
                           token=None, **kwargs):
        """Creates a Tag and associates it with metadata Record.

        Args:
            connects_to (str): UUID5 of the Record to be annotated
            name (str): Name of the new Tag
            description (str, optional): Plaintext description of the Tag
            owner (str, optional): TACC.cloud username owning the Tag and Association
            tag_owner (str, optional): TACC.cloud username owning the Tag (if different)

        Returns:
            tuple: The created or updated (TagAnnotation, Association)

        Raises:
            AnnotationError: Error prevented creation of the Tag Annotation
            AssociationError: Error occurred creating the Association
        """

        self.validate_tapis_username(owner)
        if tag_owner is not None:
            self.validate_tapis_username(tag_owner)
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
                connects_from, connects_to, note=association_note, owner=owner)

        return (anno, assoc)

    def delete_tag(self,
                   uuid,
                   keep_associations=False,
                   token=None,
                   force=False,
                   **kwargs):
        """Deletes a Tag (and, optionally, its related Associations)

        Args:
            uuid (str/list): UUID (or list) for the Tag to be deleted
            keep_associations (bool, optional): Don't delete Associations

        Returns:
            tuple: (Tags deleted, Associations deleted)
        """
        del_uuids = self.listify_uuid(uuid)
        count_deleted_tag_uuids = 0
        count_deleted_tag_uuids_list = list()
        for duuid in del_uuids:
            try:
                self.logger.info('Deleting Tag {}'.format(duuid))
                self.stores['tag_annotation'].delete_document(
                    duuid, token=token, force=force, **kwargs)
                count_deleted_tag_uuids = count_deleted_tag_uuids + 1
                count_deleted_tag_uuids_list.append(duuid)
            except Exception as exc:
                self.logger.error(
                    'Failed to delete {}: {}'.format(duuid, exc))
        self.logger.debug(
            'Deleted {} Tags'.format(count_deleted_tag_uuids))

        count_deleted_assoc_uuids = 0
        if not keep_associations:
            self.logger.info('Deleting Associations to {}'.format(duuid))
            del_associations = self._associations_for_annotation(uuid)
            del_association_uuids = list()
            del_association_uuids = [a['uuid'] for a in del_associations if a['uuid'] not in del_association_uuids]
            count_deleted_assoc_uuids = self.delete_association(
                del_association_uuids, token=token, **kwargs)

        return (count_deleted_tag_uuids, count_deleted_assoc_uuids)

    def delete_association_by_nodes(self,
                                    connects_to=None,
                                    connects_from=None,
                                    owner=None,
                                    token=None,
                                    force=False,
                                    only_visible=True,
                                    **kwargs):
        """Deletes Associations between an Annotation and one or more Records.

        Args:
            connects_from (str): UIUD for the Annotation
            connects_to (str/list): UUID (or list) for target Data Catalog record
            owner (str, optional): TACC.cloud username owning the association

        Returns:
            tuple: (0, Associations deleted)
        """

        from_uuids = self.listify_uuid(connects_from)
        to_uuids = self.listify_uuid(connects_to)

        if not len(from_uuids) > 0:
            raise ValueError('connects_from must contain one or more UUIDs')
        if not len(to_uuids) > 0:
            raise ValueError('connects_to must contain one or more UUIDs')

        query = {'connects_from': from_uuids,
                 'connects_to': to_uuids,
                 'owner': owner}

        if only_visible:
            query[self.stores['association'].DELETE_FIELD] = True

        associations = self._associations_for_annotation(
            connects_from, connects_to=to_uuids,
            owner=owner, only_visible=only_visible)
        association_uuids = [a['uuid'] for a in associations]
        self.logger.debug(
            'Up to {} associations will be deleted'.format(len(association_uuids)))
        count_deleted_uuids = self.delete_association(
            association_uuids, token=token, force=force,
            only_visible=only_visible, **kwargs)
        return tuple(0, count_deleted_uuids)

    def delete_association(self,
                           uuid=None,
                           token=None,
                           force=False,
                           **kwargs):
        """Deletes an Association by its UUID

        Args:
            uuid (str/list): Association UUID (or list) to delete

        Returns:
            tuple: (0, Associations deleted)
        """
        del_uuids = self.listify_uuid(uuid)
        count_deleted_uuids = 0
        for duuid in del_uuids:
            try:
                self.logger.info('Deleting Association {}'.format(duuid))
                self.stores['association'].delete_document(
                    duuid, token=None, force=force)
                count_deleted_uuids = count_deleted_uuids + 1
            except Exception as exc:
                self.logger.error(
                    'Failed to delete {}: {}'.format(duuid, exc))

        self.logger.debug(
            'Deleted {} Associations'.format(count_deleted_uuids))
        return tuple(0, count_deleted_uuids)

    def new_text_annotation(self,
                            connects_to=None,
                            body=None,
                            owner=None,
                            subject=None,
                            token=None,
                            **kwargs):
        """Creates a Text Note linked to a Data Catalog Record

        Args:
            connects_to (str): UUID of the target Data Catalog record
            body (str): Body of the Text Annotation (Max size: 2 kb)
            owner (str, optional): TACC.cloud username or email owner for the Text Annotation
            subject (str, optional): Subject of the Text Annotation

        Returns:
            TextAnnotation: Representation of the new Note

        Raises:
            AnnotationError: Error prevented creation of the Text Annotation
            AssociationError: Error occurred creating the final linkage
        """
        self.validate_tapis_username(owner)
        self.validate_uuid(connects_to)
        if body is None or body == '':
            raise ValueError('"body" cannot be empty or null')
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

    def reply_text_annotation(self,
                              uuid,
                              body,
                              owner=None,
                              subject=None,
                              token=None,
                              **kwargs):
        """Adds a Reply to a Text Note

        Args:
            uuid (str): UUID of the Text Annotation being replied to
            body (str): Body of the Reply (Max size: 2 kb)
            owner (str, optional): TACC.cloud username or email owner for the Reply
            subject (str, optional): Subject for the Reply (Default: Re: Parent subject)

        Returns:
            TextAnnotation: Representation of the Reply

        Raises:
            AnnotationError: Error prevented creation of the Reply
        """
        self.validate_tapis_username(owner)
        text_anno_rec = self.get_by_uuid(uuid, permissive=False)
        # Thread the subject line, just like email 💌
        if subject is None:
            orig_subject = text_anno_rec.get('subject', '')
            if orig_subject is not None:
                subject = 'Re: ' + orig_subject

        # assoc_uuid = None
        anno = self.stores['text_annotation'].new_reply(
            uuid, subject=subject, body=body,
            owner=owner, token=token)
        return TextAnnotation(self.sanitize(anno))

    def new_text_association(self, uuid,
                             record_uuid,
                             owner=None,
                             token=None,
                             **kwargs):
        """Associates a Text Annotation with 1+ other metadata records
        """
        if typeduuid.get_uuidtype(uuid) != 'text_annotation':
            raise ValueError('Function only accepts tag UUIDs')
        return self._new_annotation_association(
            uuid, record_uuid,
            owner=owner, token=token, **kwargs)

# Create a Text Anno AND bind to record in one shot
# Create a Text Anno AND bind as child of another in one shot
# Validate usernames via Agave call
# Create and retire Tag and Text associations
# Batch purge by target, source, username
