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

class ChallengeUpdateFailure(CatalogUpdateFailure):
    pass

class ChallengeDocument(DocumentSchema):
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
        super(ChallengeDocument, self).__init__(**params)
        self.update_id()

class ChallengeStore(BaseStore):
    TYPED_UUID_TYPE = 'challenge_problem'
    def __init__(self, mongodb, config, session=None, **kwargs):
        super(ChallengeStore, self).__init__(mongodb, config, session)
        self.schema = ChallengeDocument(**kwargs).to_dict()

        coll = self.collections.get('challenges')
        if self.debug:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()
