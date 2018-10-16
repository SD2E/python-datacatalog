from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

from basestore import *
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

    def to_dict(self, private_prefix='_', document=False):
        my_dict = super(MeasurementDocument, self).to_dict(private_prefix, document)
        # In standalone document mode, files are not embededed as subdoc
        # but instead are linked via the child_of relationship
        if document is False:
            for f in ['files']:
                try:
                    del my_dict['properties'][f]
                except Exception:
                    pass
                # filter out requirement for files, too
                try:
                    my_dict['required'].remove(f)
                except Exception:
                    pass
        return my_dict

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
