import os
import json
from datacatalog.tokens import (
    validate_token, validate_admin_token)
from ..schemabase import EventBaseSchema
from ..anno import (DeletedRecordCounts, AssociatedAnnotation)

class TagAnnotationDeleteSchema(EventBaseSchema):
    DEFAULT_DOCUMENT_NAME = 'delete.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'rb'))
        super().__init__(**j)
        self.update_id()

class Schema(TagAnnotationDeleteSchema):
    pass

def get_schema():
    return TagAnnotationDeleteSchema()

def action(self, body, token=None):
    self.logger.info('event.delete')
    validate_admin_token(token, permissive=False)
    return delete_tag(self, token=token, **body)

def delete_tag(self, uuid=None, keep_associations=False,
               token=None, force=False, **kwargs):
    """Deletes a Tag and its related Associations

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

    count_deleted_assoc = 0
    if not keep_associations:
        self.logger.info('Deleting Associations to {}'.format(duuid))
        del_associations = self._associations_for_annotation(uuid)
        del_association_uuids = list()
        del_association_uuids = [a['uuid'] for a in del_associations if a['uuid'] not in del_association_uuids]
        count_deleted_assoc = self.delete_association(
            del_association_uuids, token=token, **kwargs)
        count_deleted_assoc = count_deleted_assoc.associations

    return DeletedRecordCounts(count_deleted_tag_uuids, count_deleted_assoc)
