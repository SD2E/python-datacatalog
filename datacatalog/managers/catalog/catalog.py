import json
import importlib
import inspect
import itertools
import os
import sys
import copy
from pprint import pprint

from ... import linkedstores
from ... import jsonschemas
from ...identifiers import typeduuid
from ..common import Manager, ManagerError

class CatalogManagerError(ManagerError):
    pass

class CatalogManager(Manager):
    """Supports operations spanning multiple LinkedStore collections"""

    # def get_uuidtype(self, uuid):
    #     """Identify the named type for a given UUID

    #     Args:
    #         uuid (str): UUID to classify by type

    #     Returns:
    #         str: Named type of the UUID
    #     """
    #     typeduuid.validate(uuid)
    #     return typeduuid.get_uuidtype(uuid)

    # def get_by_uuid(self, uuid):
    #     """Returns a LinkedStore document by UUID

    #     Args:
    #         uuid (str): UUID of the document to retrieve

    #     Returns:
    #         dict: The document that was retrieved
    #     """
    #     storename = self.get_uuidtype(uuid)
    #     return self.sanitize(
    #         self.stores[storename].find_one_by_uuid(uuid))

    # def get_by_identifier(self, identifier_string):
    #     """Search LinkedStores for a string identifier

    #     Args:
    #         identifier_string (str): An identifier string
    #     Returns:
    #         dict: The document that was retrieved
    #     """
    #     # TODO - use any namespacing in identifier_string to select intitial store to query
    #     for sname, store in self.stores.items():
    #         for i in store.get_identifiers():
    #             query = {i: identifier_string}
    #             resp = store.coll.find_one(query)
    #             if resp is not None:
    #                 return self.sanitize(resp)
    #     return None

    # def get_by_uuids(self, uuids):
    #     """Returns a list of LinkedStore documents by UUID

    #     Args:
    #         uuids (list): List of document UUIDs

    #     Returns:
    #         list The document that was retrieved
    #     """
    #     recs = list()
    #     for uuid in uuids:
    #         resp = self.get_by_uuid(uuid)
    #         if resp is not None:
    #             recs.append(resp)
    #     sorted_recs = sorted(recs, key=lambda k: k['uuid'])
    #     return sorted_recs

    def delete_by_uuid(self, uuid, token=None):
        """Deletes LinkedStore document and all linked references

        Args:
            uuid (str): UUID of the document to fully delete
            token (str, optional): Update token

        Returns:
            bool: Whether delete was successful or not
        """
        storename = self.get_uuidtype(uuid)
        self.stores[storename].coll.find_one_and_delete({'uuid': uuid})
        for name, store in self.stores.items():
            try:
                for linkage in store.LINK_FIELDS:
                    store.coll.update_many({linkage: {'$in': [uuid]}}, {'$pull': {linkage: uuid}})
            except Exception:
                raise
        return True

    def link(self, uuid1, uuid2, type='child_of', token=None):
        return False

    def unlink(self, uuid1, uuid2, type='child_of', token=None):
        return False
