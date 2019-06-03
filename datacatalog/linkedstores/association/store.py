from datacatalog import linkages
from datacatalog.identifiers import typeduuid, tacc
from datacatalog.linkedstores import annotations
from datacatalog.linkedstores.basestore import (LinkedStore, SoftDelete, strategies)
from .document import AssociationSchema, AssociationDocument
from .exceptions import AssociationError

class AssociationStore(SoftDelete, LinkedStore):
    """Manage association records"""
    LINK_FIELDS = [linkages.CONNECTS_FROM, linkages.CONNECTS_TO]

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(AssociationStore, self).__init__(mongodb, config, session)
        schema = AssociationSchema(**kwargs)
        super(AssociationStore, self).update_attrs(schema)
        self._enforce_auth = True
        self.setup(update_indexes=kwargs.get('update_indexes', False))

    def associate(self, annotation_uuid, record_uuid, owner=None, token=None):
        """Create an association between an annotation and a metadata record

        Arguments:
            annotation_uuid (str): UUID5 for the annotation (connects_from)
            record_uuid (str): UUID5 for a metadata record (connects_to)
            owner (str, optional): TACC.cloud username owning the association

        Returns:
            str: UUID5 of the resulting association

        Raises:
            ValueError: Either the annotation or record UUID was the wrong type
            AssociationError: A failure prevented the association from being created
        """
        if typeduuid.get_uuidtype(annotation_uuid) not in (
                'tag_annotation', 'text_annotation'):
            raise ValueError('Source must be an annotation UUID')
        if typeduuid.get_uuidtype(record_uuid) not in annotations.TARGET_TYPES:
            raise ValueError('Target UUID not an allowed type')
        # Validate username by format. Save formal validation for a manager
        # class where we can reasonbly expect an active Agave or TAS client
        tacc.username.validate(owner, permissive=False)
        doc = AssociationDocument(owner=owner,
                                  connects_to=record_uuid,
                                  connects_from=annotation_uuid)
        resp = self.add_update_document(doc, strategy=strategies.REPLACE,
                                        token=token)
        return self.undelete(resp.get('uuid'), token=token)

    def dissociate(self, annotation_uuid, record_uuid, owner=None, token=None):
        # Soft Delete
        # Find distinct document from the two UUIDs then soft-delete it
        query = {'connects_from': annotation_uuid,
                 'connects_to': record_uuid,
                 'owner': owner}
        rec_uuid = self.coll.find_one(query).get('uuid', None)
        if rec_uuid is not None:
            return self.delete_document(rec_uuid, token=token)
        else:
            raise AssociationError('Unable to find or delete this association')


class StoreInterface(AssociationStore):
    pass
