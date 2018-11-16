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

from ...dicthelpers import data_merge
from ...utils import time_stamp
from .documentschema import DocumentSchema

class HeritableDocumentSchema(DocumentSchema):
    """Extends DocumentSchema with inheritance from parent object's JSON schema

    HeritableDocumentSchema objects validate build a schema from their local
    `document.json`, but that document is layered over the contents of the
    schema defined by the root class using a right-favoring merge. Filters,
    which are used in formatting object vs document schemas, are not inherited.
    """
    DEFAULT_DOCUMENT_NAME = 'document.json'
    """Filename of the JSON schema document, relative to __file__."""
    DEFAULT_FILTERS_NAME = 'filters.json'
    """Filename of the JSON schema filters document, relative to __file__."""

    def __init__(self, inheritance=True, document=DEFAULT_DOCUMENT_NAME,
                 filters=DEFAULT_FILTERS_NAME, **kwargs):
        schemaj = kwargs
        try:
            modfile = inspect.getfile(self.__class__)
            schemafile = os.path.join(os.path.dirname(modfile), document)
            schemaj = json.load(open(schemafile, 'r'))
            if inheritance is True:
                parent_modfile = inspect.getfile(self.__class__.__bases__[0])
                parent_schemafile = os.path.join(os.path.dirname(parent_modfile), document)
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
