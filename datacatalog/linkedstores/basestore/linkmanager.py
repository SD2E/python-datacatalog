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
            LinkageManagerError: Returned if an invalid relation type or
            unknown UUID is encountered, or if linkage count policy is violated
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
        link_uuid_filt_len = len(link_uuid_filt)

        max_links_by_name = self.get_linkages()[relation]
        count_links = -1

        if max_links_by_name >= 0:
            # Count current
            count_links = self.coll.find_one({'uuid': uuid}).get(relation, [])
            self.logger.debug('{} extant {} linkages found'.format(
                count_links, relation))

        if max_links_by_name == 1:
            # Deal with Max == 1 - Replace existing if one new link is provided
            if link_uuid_filt_len > max_links_by_name:
                raise LinkageManagerError('Cannot add {} links since policy restricts the maximum to 1'.format(link_uuid_filt_len))
            # Allow one link at a time, so reset linkage array to empty
            self.logger.debug('current linkage will be replaced 1:1')
            self.coll.update_one({'uuid': uuid},
                                 {'$set': {relation: []}})
        elif count_links + link_uuid_filt_len > max_links_by_name:
            # Test projected number of links against policy before allowing
            # the linkage to take place below
            raise LinkageManagerError(
                'Cannot add {} links(s) as that exceeds policy for {}. '.format(
                    link_uuid_filt_len, relation) +
                'Remove some linkages via remove_link() before ' +
                'attempting creating additonal linkages.')

        # Add to array
        self.logger.info('now adding linkage (if it does not exist)')
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
            ValueError: Returned if an invalid relation type or unknown UUID is encountered
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
                raise ValueError(
                    'Relationship "{}" not available in document {}'.format(
                        relation, uuid))
