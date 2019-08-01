import collections
import json
import os
from ..common import Manager
from copy import deepcopy
from pymongo.cursor import Cursor
from datacatalog.jsonschemas import JSONSchemaBaseObject
from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.identifiers import typeduuid
from datacatalog.linkedstores.association import Association, AssociationError
from datacatalog.linkedstores.annotations import AnnotationError
from datacatalog.linkedstores.annotations.tag import (
    TagAnnotation, TagAnnotationDocument)
from datacatalog.linkedstores.annotations.text import TextAnnotation
from datacatalog import settings

DeletedRecordCounts = collections.namedtuple(
    'DeletedRecordCounts', 'annotations associations')
AssociatedAnnotation = collections.namedtuple(
    'AssociatedAnnotation', 'annotation association')
AnnotationResponse = collections.namedtuple(
    'AnnotationResponse', 'record_uuid annotation_uuid association_uuid')

class AnnotationManagerSchema(JSONSchemaBaseObject):
    """Defines the baseline Annotation Manager event"""
    DEFAULT_DOCUMENT_NAME = 'anno.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'rb'))
        super(AnnotationManagerSchema, self).__init__(**j)
        self.update_id()

class AnnotationManager(Manager):

    PUBLIC_USER = settings.TAPIS_ANY_AUTHENTICATED_USERNAME

    def __init__(self, mongodb, agave=None, *args, **kwargs):
        Manager.__init__(self, mongodb, agave=agave, *args, **kwargs)

    def _new_annotation_association(self,
                                    anno_uuid,
                                    record_uuid,
                                    owner=None,
                                    note='',
                                    token=None,
                                    **kwargs):
        """Private: Creates an Association between a Record and an Annotation.
        """
        self.validate_tapis_username(owner, permissive=True)
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
        return tags_all

    # def new_tag_annotation(self,
    #                        connects_to=None,
    #                        name=None,
    #                        owner=None,
    #                        description='',
    #                        tag_owner=None,
    #                        association_note='',
    #                        token=None, **kwargs):
    #     """Creates a Tag and associates it with metadata Record.

    #     Args:
    #         connects_to (str): UUID5 of the Record to be annotated
    #         name (str): Name of the new Tag
    #         description (str, optional): Plaintext description of the Tag
    #         owner (str, optional): TACC.cloud username owning the Tag and Association
    #         tag_owner (str, optional): TACC.cloud username owning the Tag (if different)

    #     Returns:
    #         tuple: The created or updated (TagAnnotation, Association)

    #     Raises:
    #         AnnotationError: Error prevented creation of the Tag Annotation
    #         AssociationError: Error occurred creating the Association
    #     """

    #     self.validate_tapis_username(owner)
    #     if tag_owner is not None:
    #         self.validate_tapis_username(tag_owner)
    #     else:
    #         tag_owner = owner

    #     connects_from = None
    #     anno = self.stores['tag_annotation'].new_tag(name=name,
    #                                                  description=description,
    #                                                  owner=tag_owner,
    #                                                  token=token,
    #                                                  **kwargs)
    #     connects_from = anno.get('uuid', None)
    #     assoc = None
    #     if connects_from is not None:
    #         assoc = self.stores['association'].associate(
    #             connects_from, connects_to, note=association_note, owner=owner)

    #     return AssociatedAnnotation(anno, assoc)

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
        return DeletedRecordCounts(0, count_deleted_uuids)

# Create a Text Anno AND bind to record in one shot
# Create a Text Anno AND bind as child of another in one shot
# Validate usernames via Agave call
# Create and retire Tag and Text associations
# Batch purge by target, source, username
