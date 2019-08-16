import os
import sys
import inspect
import json
import copy
import datetime
import base64

from pprint import pprint
from jsondiff import diff

from .store import LinkedStore
from ...settings import MONGO_DELETE_FIELD

class SoftDelete(LinkedStore):
    """Adds field-based soft delete to a LinkedStore"""

    DELETE_FIELD = MONGO_DELETE_FIELD

    def add_document(self, document, token=None, force=True):
        if force is True:
            document[self.DELETE_FIELD] = True
        return super(SoftDelete, self).add_document(document, token=token)

    def delete_document(self, uuid, token=None, force=False):
        if force is False:
            try:
                resp = self.coll.update({'uuid': uuid},
                                        {'$set': {self.DELETE_FIELD: False}})
                if resp is not None:
                    return self.find_one_by_uuid(uuid)
            except Exception:
                raise
        else:
            return super(SoftDelete, self).delete_document(uuid, token)

    def undelete(self, uuid, token=None, force=False):
        if force is False:
            resp = self.coll.update({'uuid': uuid},
                                    {'$set': {self.DELETE_FIELD: True}})
            if resp is not None:
                return self.find_one_by_uuid(uuid)
        else:
            raise NotImplementedError('SoftDelete is not available')

    # TODO - Implement filters on _visible for update_delete and write_key
    # TODO - Figure out what to do in the case of the replace strategy
