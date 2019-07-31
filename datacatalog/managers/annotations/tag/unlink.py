import os
import json
from ..schemabase import EventBaseSchema
from datacatalog.tokens import (
    validate_token, validate_admin_token)
from ..anno import (DeletedRecordCounts, AssociatedAnnotation)

class TagAnnotationUnlinkSchema(EventBaseSchema):
    DEFAULT_DOCUMENT_NAME = 'unlink.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'rb'))
        super().__init__(**j)
        self.update_id()

class Schema(TagAnnotationUnlinkSchema):
    pass

def action(self, body, token=None):
    self.logger.info('event.unlink')
    validate_admin_token(token, permissive=False)
    return delete_association_by_nodes(self, token=token, **body)

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
    return DeletedRecordCounts(0, count_deleted_uuids)
