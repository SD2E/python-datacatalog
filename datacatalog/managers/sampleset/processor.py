import json
import importlib
import inspect
import itertools
from pprint import pprint

from . import jsonschemas
from . import linkedstores

# from . import linkedstores

# Determine challenge problem
# Determine experiment
# Iterate over samples

def dynamic_import(module, package=None):
    # print(module, package)
    return importlib.import_module(module, package=package)

class SampleSetProcessor(object):
    def __init__(self, mongodb_settings, samples_file=None):
        # Assemble dict of stores keyed by classname
        self.stores = SampleSetProcessor.init_stores(mongodb_settings)
        self.document = dict()
        if samples_file is not None:
            setattr(self, 'document', self.load_file(samples_file))

    @classmethod
    def init_stores(cls, mongodb_settings):
        # Assemble dict of stores keyed):
        stores = dict()
        # pprint(globals())
        # pprint(dir(linkedstores))
        print(tuple(jsonschemas.schemas.STORE_SCHEMAS))
        for pkg in tuple(jsonschemas.schemas.STORE_SCHEMAS):
            try:
                m = dynamic_import(pkg)
                store = m.StoreInterface(mongodb_settings)
                store_name = getattr(store, 'uuid_type')
                store_basename = store_name.split('.')[-1]
                stores[store_basename] = store
            except ModuleNotFoundError as mexc:
                print('Module not found: {}'.format(pkg), mexc)
        return stores

    def load_file(self, sampleset_file):
        jsonfile = open(sampleset_file, 'r')
        jsondoc = json.load(jsonfile)
        return jsondoc

    def get(self, doctype, identifier, identifier_value):
        query = {identifier: identifier_value}
        return self.stores[doctype].find_one_by_id(**query)

    def get_challenge_problem(self):
        doc_value = self.document.get('challenge_problem', 'UNKNOWN')
        cp = self.get('challenge_problem', 'id', doc_value)
        setattr(self, 'challenge_problem', cp)
        return cp

    def get_challenge_problem_id(self):
        return self.get_challenge_problem()['id']

    def get_experiment(self):
        doc_value = self.document.get('experiment_reference', 'UNKNOWN')
        print('EXPT ', doc_value)
        ex = self.get('experiment', 'id', doc_value)
        print('EX', ex)
        setattr(self, 'experiment', ex)
        return ex

    def get_experiment_id(self):
        return self.get_experiment()['id']

    def process(self):
        challenge_problem_id = self.get_challenge_problem_id()
        experiment_id = self.get_experiment_id()
