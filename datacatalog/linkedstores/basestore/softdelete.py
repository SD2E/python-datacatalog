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

class SoftDelete(LinkedStore):
    """Adds field-based soft delete to a LinkedStore"""

    def add_document(self, document, token=None, soft=True):
        if soft is True:
            document['_visible'] = True
        return super(SoftDelete, self).add_document(document, token=token)

    def delete_document(self, uuid, token=None, soft=True):
        if soft is True:
            return self.write_key(uuid, '_visible', False, token)
        else:
            return super(SoftDelete, self).delete_document(uuid, token)

    def undelete(self, uuid, token=None):
        return self.write_key(uuid, '_visible', True, token)

    # TODO - Implement filters on _visible for update_delete and write_key
    # TODO - Figure out what to do in the case of the replace strategy
