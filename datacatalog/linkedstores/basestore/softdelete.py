from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object

import os
import sys
import inspect
import json
import copy
import datetime
import base64

from pprint import pprint
from jsondiff import diff

from .store import BaseStore

class SoftDelete(BaseStore):
    """A mix-in that adds field-based delete to a LinkedStore"""

    def delete_document(self, uuid, token=None, soft=True):
        if soft is True:
            return self.write_key(uuid, '_visible', False, token)
        else:
            return super(SoftDelete, self).delete_document(uuid, token)

    def undelete(self, uuid, token=None):
        return self.write_key(uuid, '_visible', True, token)

    # TODO - Implement filters on _visible for update_delete and write_key
