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

from pprint import pprint
from dicthelpers import data_merge
from utils import time_stamp

from .documentschema import DocumentSchema

class HeritableDocumentSchema(DocumentSchema):
    DEFAULT_DOCUMENT_NAME = 'document.json'

    def __init__(self, inheritance=True, filename=DEFAULT_DOCUMENT_NAME, **kwargs):
        schemaj = dict()
        try:
            modfile = inspect.getfile(self.__class__)
            schemafile = os.path.join(os.path.dirname(modfile), filename)
            schemaj = json.load(open(schemafile, 'r'))
            if inheritance is True:
                parent_modfile = inspect.getfile(self.__class__.__bases__[0])
                parent_schemafile = os.path.join(os.path.dirname(parent_modfile), filename)
                try:
                    pschemaj = json.load(open(parent_schemafile, 'r'))
                except Exception:
                    pschemaj = dict()
                schemaj = data_merge(pschemaj, schemaj)
        except Exception:
            raise
        params = {**schemaj, **kwargs}
        super(HeritableDocumentSchema, self).__init__(**params)
        # pprint(self.__dict__)
        self.update_id()
