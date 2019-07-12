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
        """Private method to create a generic association record
        """
        self.validate_tapis_username(owner)
        # Either a single or list of target UUIDs is allowed. A list of
        # ssociations is returned in either case. This allows batch association
        # of a tag to multiple UUIDs

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
        return associations

    def _associations_for_annotation(self, uuid,
                                     owner=None,
                                     only_visible=True):
        """Private method to find Associations referencing an Annotation

        Arguments:
            uuid (str): UUID of an Annotation
            only_visible (bool, optional): Only return items not marked as deleted

        Returns:
            list: Unique associations linked to the specified annotation
        """
        self.logger.info('Finding associations for annotation {}'.format(uuid))

        query = {'connects_from': uuid}
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
                len(found_associations), uuid))

        return found_associations

    def new_tag(self,
                name=None,
                owner=None,
                description='',
                token=None, **kwargs):
        """Create a Tag

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

    def delete_tag(self, uuid,
                   keep_associations=False,
                   token=None,
                   **kwargs):
        """Delete a Tag (and related Associations)

        Args:
            uuid (str, list): UUID (or list) for the Tag to be deleted
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
                    duuid, token=token, **kwargs)
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

    def delete_association(self, uuid,
                           token=None,
                           **kwargs):
        """Delete an Association

        Args:
            uuid (str, list): Association UUID (or list) to delete

        Returns:
            int: Count of Associations deleted
        """
        del_uuids = self.listify_uuid(uuid)
        count_deleted_uuids = 0
        for duuid in del_uuids:
            try:
                self.logger.info('Deleting Association {}'.format(duuid))
                self.stores['association'].delete_document(
                    duuid, token=None)
                count_deleted_uuids = count_deleted_uuids + 1
            except Exception as exc:
                self.logger.error(
                    'Failed to delete {}: {}'.format(duuid, exc))

        self.logger.debug(
            'Deleted {} Associations'.format(count_deleted_uuids))
        return count_deleted_uuids

    def new_tag_association(self, anno_uuid,
                            record_uuid,
                            owner=None,
                            token=None, **kwargs):
        """Associate a Tag with one or more Data Catalog records

        Args:
            anno_uuid (str): UIUD for the Tag (connects_from)
            record_uuid (str, list): UUID (or list) for taget Data Catalog record (connects_to)
            owner (str, optional): TACC.cloud username owning the association

        Returns:
            list: List of one or more created Associations
        """
        if typeduuid.get_uuidtype(anno_uuid) != 'tag_annotation':
            raise ValueError('Function only accepts tag UUIDs')
        return self._new_annotation_association(
            anno_uuid, record_uuid,
            owner=owner, token=token, **kwargs)

    def tags_list(self,
                  limit=None,
                  skip=None,
                  public=True,
                  private=True,
                  visible=True):
        """Retrieve the known list of Tags

        Args:
            limit (int, optional): Maximum number of records to return
            skip (int, optional): Skip this many matching records
            public (bool, optional): Return public tags
            private (bool, optional): Return private (to user) tags
            visible (bool, optional): Return only tags that are not soft-deleted

        Returns:
            list: List of dict objects representing each tag
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
        return tags_all

    def new_tag_annotation(self, record_uuid,
                           name=None,
                           owner=None,
                           description='',
                           tag_owner=None,
                           association_note='',
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
            AssociationError: Error occurred creating the Association
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
                anno_uuid, record_uuid, note=association_note, owner=owner)
            assoc_uuid = assoc.get('uuid', None)

        a = AnnotationResponse(annotation_uuid=anno_uuid,
                               association_uuid=assoc_uuid,
                               record_uuid=record_uuid)
        return a

    def publish_tag(self, uuid,
                    keep_associations=True,
                    remove_original=False,
                    token=None,
                    **kwargs):
        """Copy a Tag into the public namespace

        Args:
            uuid (str): UUID of the Tag to publish
            associations (bool, optional): Include the Tag's Associations when publishing
            remove_original (bool, optional): Delete the original Tag after publication

        Returns:
            dict: Representation of the public Tag
        """
        anno = self.stores['tag_annotation'].find_one_by_uuid(uuid)
        if anno is None:
            raise ValueError(
                'Tag with UUID {} does not exist'.format(uuid))
        if anno.get('owner', None) == self.PUBLIC_USER:
            return anno

        self.logger.info('Cloning Tag {}'.format(uuid))
        new_anno = TagAnnotationDocument(
            name=anno['name'],
            description=anno['description'],
            owner=self.PUBLIC_USER)
        # Impdepotent clone
        resp = self.stores['tag_annotation'].add_update_document(
            new_anno, token=None)
        resp_2 = self.stores['tag_annotation'].undelete(
            resp['uuid'], token=token)
        cloned_tag_uuid = resp_2.get('uuid')
        self.logger.info('Cloned Tag.uuid: {}'.format(cloned_tag_uuid))

        if keep_associations:
            # Fetch assoc for original tag
            clonable_associations = self._associations_for_annotation(uuid)
            self.logger.info(
                'Cloning up to {} Associations for Tag {}'.format(
                    len(clonable_associations), uuid))
            for clone_assoc in clonable_associations:
                # New_tag_association can accept a list for cloned_assoc_uuids
                # saving us a loop in this function
                self.new_tag_association(clone_assoc['connects_to'],    cloned_tag_uuid, note=clone_assoc.get('note', ''), owner=self.PUBLIC_USER)

        # We do not return any details on the associations,
        # only the cloned tag
        return TagAnnotation(self.sanitize(resp_2))

    def unpublish_tag(self, uuid,
                      associations=True,
                      token=None, **kwargs):
        """Remove a Tag from the public namespace

        Args:
            tag_uuid (str): UUID of the Tag to unpublish

        Returns:
            tuple: (Tag UUID, Success)
        """
        anno = self.stores['tag_annotation'].find_one_by_uuid(uuid)
        if anno is None:
            raise ValueError(
                'Tag with UUID {} does not exist'.format(uuid))
        if anno.get('owner', None) != self.PUBLIC_USER:
            raise ValueError('Only public Tags can be unpublished')

        try:
            self.stores['tag_annotation'].delete_document(
                uuid, token=None)
            self.delete_association(uuid, token=token)
            return (uuid, True)
        except Exception as exc:
            self.logger.error(
                'Failed to unpublish Tag {}: {}'.format(uuid, exc))

        return (uuid, False)

    def new_text_annotation(self,
                            record_uuid,
                            body,
                            owner=None,
                            subject=None,
                            token=None,
                            **kwargs):
        """Create a Text Annotation linked to a Data Catalog record

        Args:
            record_uuid (str): UUID of the target Data Catalog record
            body (str): Body of the Text Annotation (Max size: 2 kb)
            owner (str, optional): TACC.cloud username or email owner for the Text Annotation
            subject (str, optional): Subject of the Text Annotation

        Returns:
            dict: Representation of the new Text Annotation

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

    def reply_text_annotation(self,
                              uuid,
                              body,
                              owner=None,
                              subject=None,
                              token=None,
                              **kwargs):
        """Reply to a Text Annotation

        Args:
            uuid (str): UUID for the Text Annotation being responded to
            body (str): Body of the Reply (Max size: 2 kb)
            owner (str, optional): TACC.cloud username or email owner for the Reply
            subject (str, optional): Subject for the Reply (Default: Re: Parent subject)

        Returns:
            dict: Representation of the Reply

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
