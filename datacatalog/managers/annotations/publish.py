"""Implements a publish and unpublish mix-in for AnnotationManager
"""
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

class AnnotationPublicationManager(Manager):

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
