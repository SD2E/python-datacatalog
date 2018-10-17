from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import inspect
import json
import os
import sys

from ..basestore import BaseStore, CatalogUpdateFailure, DocumentSchema
from dicthelpers import data_merge
from pprint import pprint

class MeasurementUpdateFailure(CatalogUpdateFailure):
    pass

class MeasurementDocument(DocumentSchema):
    def __init__(self, inheritance=True, **kwargs):
        schemaj = dict()
        try:
            modfile = inspect.getfile(self.__class__)
            schemafile = os.path.join(os.path.dirname(modfile), 'document.json')
            schemaj = json.load(open(schemafile, 'r'))
            if inheritance is True:
                parent_modfile = inspect.getfile(self.__class__.__bases__[0])
                parent_schemafile = os.path.join(os.path.dirname(parent_modfile), 'document.json')
                pschemaj = json.load(open(parent_schemafile, 'r'))
                schemaj = data_merge(pschemaj, schemaj)
        except:
            raise
        params = {**schemaj, **kwargs}
        super(MeasurementDocument, self).__init__(**params)
        self.update_id()

class MeasurementStore(BaseStore):
    TYPED_UUID_TYPE = 'measurement'

    def __init__(self, mongodb, config, session=None, **kwargs):
        super(MeasurementStore, self).__init__(mongodb, config, session)
        self.schema = MeasurementDocument(**kwargs).to_dict()

        coll = self.collections.get('measurements')
        if self.debug:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()
