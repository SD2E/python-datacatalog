from datacatalog import linkages
from datacatalog.identifiers import typeduuid

class LinkageManagerError(Exception):
    pass

class LinkageManager(object):
    def add_link(self, uuid, linked_uuid, relation=linkages.CHILD_OF, token=None):
        """Link a Data Catalog record with one or more records by UUID

        Args:
            uuid (str): UUID of the subject record
            linked_uuid (str, list): UUID (or list) of the object record(s)
            relation (str, optional): Name of the relation add
            token (str): String token authorizing edits to the subject record

        Returns:
            dict: Contents of the revised Data Catalog record

        Raises:
            LinkageManagerError: Returned if an invalid relation type or unknown UUID is encountered
        """
        # Validate relation
        relation = linkages.Linkage(relation)
        if relation not in self.LINK_FIELDS:
            self.logger.warning('{} is not a known linkage for {}'.format(relation, self.uuid_type))
            return False

        # Transform single UUID string into list
        if isinstance(linked_uuid, str):
            linked_uuid = [linked_uuid]
        elif linked_uuid is None:
            # Allows the futile case in case
            linked_uuid = list()

        self.logger.debug("writing linkage '{}' for {}".format(relation, uuid))
        self.logger.debug("data: '{}'".format(linked_uuid))

        # Validate UUIDs and not self
        link_uuid_filt = [u for u in linked_uuid if typeduuid.validate(
            u, permissive=True) and u != uuid]
        
        resp = self.coll.update_one({'uuid': uuid}, 
                                    {'$addToSet': {relation: {'$each': link_uuid_filt}}})
        if resp.acknowledged:
            return True
        else:
            raise LinkageManagerError('Failed to establish linkage')

    def remove_link(self, uuid, linked_uuid, relation=linkages.CHILD_OF, token=None):
        """Unlink one Data Catalog record from another

        Args:
            uuid (str): UUID of the subject record
            linked_uuid (str): UUID of the object record
            relation (str, optional): Name of the relation to remove
            token (str): String token authorizing edits to the subject record

        Returns:
            dict: Contents of the revised Data Catalog record

        Raises:
            CatalogError: Returned if an invalid relation type or unknown UUID is encountered
        """
        # Validate relation
        relation = linkages.Linkage(relation)
        if relation not in self.LINK_FIELDS:
            self.logger.warning('{} is not a known linkage for {}'.format(relation, self.uuid_type))
            return False

        # Transform single UUID string into list
        if isinstance(linked_uuid, str):
            linked_uuid = [linked_uuid]
        elif linked_uuid is None:
            # Allows the futile case in case
            linked_uuid = list()

        # Validate UUIDs and not self
        link_uuid_filt = [u for u in linked_uuid if typeduuid.validate(
            u, permissive=True) and u != uuid]

        result = False
        for link_id in link_uuid_filt:
            self.logger.debug('removing {} from {}.{}'.format(link_id, uuid, relation))
            resp = self.coll.update_one({'uuid': uuid}, 
                                        {'$pull': {relation: link_id}})
            self.logger.debug('response: {}'.format(resp.modified_count))
            result = result or resp.acknowledged
  
        if result:
            return True
        else:
            raise LinkageManagerError('Failed to remove linkage')

    def get_links(self, uuid, relation='child_of'):
        """Return linkages to this LinkedStore

        Return a list of typed UUIDs representing all connections between this
        LinkedStore and other LinkedStores. This list can be traversed to return
        a list of all LinkedStore objects using `datacatalog.managers.catalog.get()`

        Args:
            uuid (str): The UUID of the LinkedStore document to query
            relation (str, optional): The linkage relationship to return
        Returns:
            list: A list of typed UUIDs that establish relationhips to other LinkedStores
        """
        doc = self.find_one_by_uuid(uuid)
        if doc is not None:
            if relation in list(doc.keys()):
                return doc.get(relation)
            if relation in list(self.document_schema['properties'].keys()):
                # The relationship could exist as per the schema but is not defined
                return list()
            else:
                raise CatalogError(
                    'Relationship "{}" not available in document {}'.format(
                        relation, uuid))
