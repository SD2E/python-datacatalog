import json
import importlib
import inspect
import itertools
import os
import sys
from pprint import pprint

from . import jsonschemas
from . import linkedstores

def dynamic_import(module, package=None):
    # print(module, package)
    return importlib.import_module(module, package=package)

class UnknownReference(linkedstores.basestore.CatalogError):
    pass

class SampleSetProcessor(object):
    def __init__(self, mongodb_settings, samples_file=None, path_prefix='/uploads'):
        # Assemble dict of stores keyed by classname
        self.stores = SampleSetProcessor.init_stores(mongodb_settings)
        self.document = dict()
        self.prefix = path_prefix
        if samples_file is not None:
            setattr(self, 'document', self.load_file(samples_file))
            setattr(self, 'challenge_problem', self._challenge_problem())
            setattr(self, 'experiment', self._experiment())
            setattr(self, '_samples', self._samples())

    @classmethod
    def init_stores(cls, mongodb_settings):
        # Assemble dict of stores keyed):
        stores = dict()
        for pkg in tuple(jsonschemas.schemas.STORE_SCHEMAS):
            try:
                m = dynamic_import(pkg)
                store = m.StoreInterface(mongodb_settings)
                store_name = getattr(store, 'schema_name')
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
        resp = self.stores[doctype].find_one_by_id(**query)
        if resp is None:
            raise UnknownReference('Unable to get {}.{}={}'.format(doctype, identifier, identifier_value))
        else:
            return resp

    def _challenge_problem(self):
        doc_value = self.document.get('challenge_problem', 'UNKNOWN')
        challenge_problem = self.get('challenge_problem', 'id', doc_value)
        return challenge_problem

    def _experiment(self):
        doc_value = self.document.get('experiment_reference', 'UNKNOWN')
        experiment = self.get('experiment', 'experiment_id', doc_value)
        return experiment

    def _samples(self):
        samples_list = self.document.get('samples', [])
        return samples_list

    def process_samples(self, parent_uuid=None):
        for sample in self._samples:
            if 'child_of' in sample:
                sample['child_of'].append(parent_uuid)
            else:
                sample['child_of'] = [parent_uuid]
            measurements = sample.pop('measurements')
            resp = self.stores['sample'].add_update_document(sample)
            parent_uuid = resp['uuid']
            self.process_measurements(measurements, parent_uuid)
        return True

    def process_measurements(self, measurements, parent_uuid=None):
        for meas in measurements:
            if 'child_of' in meas:
                meas['child_of'].append(parent_uuid)
            else:
                meas['child_of'] = [parent_uuid]
            files = meas.pop('files')
            resp = self.stores['measurement'].add_update_document(meas)
            parent_uuid = resp['uuid']
            self.process_files(files, parent_uuid)
        return True

    def process_files(self, files, parent_uuid=None):
        for file in files:
            file['name'] = self.contextualize(file['name'])
            if 'child_of' in file:
                file['child_of'].append(parent_uuid)
            else:
                file['child_of'] = [parent_uuid]
            self.stores['file'].add_update_document(file)
        return True

    def contextualize(self, filename):
        if filename.startswith('/'):
            filename = filename[1:]
        return os.path.join(self.prefix, filename)

    def get_challenge_problem_id(self):
        return self.challenge_problem['id']

    def get_experiment_id(self):
        return self.experiment['experiment_id']

    def get_experiment_uuid(self):
        return self.experiment['uuid']

    def process(self):
        return self.process_samples(self.get_experiment_uuid())
