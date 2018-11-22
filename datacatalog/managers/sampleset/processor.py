import json
import importlib
import inspect
import itertools
import os
import sys
from pprint import pprint

from ... import linkedstores
from ... import jsonschemas
# from ... import linkedstores

def dynamic_import(module, package='datacatalog'):
    return importlib.import_module(module, package=package)

class UnknownReference(linkedstores.basestore.CatalogError):
    pass

class SampleSetProcessorError(linkedstores.basestore.CatalogError):
    pass

class SampleSetProcessor(object):
    """Manager class to process and load sample set JSON documents"""

    def __init__(self, mongodb_settings, samples_file=None, path_prefix='/uploads'):
        # Assemble dict of stores keyed by classname
        self.stores = SampleSetProcessor.init_stores(mongodb_settings)
        self.document = dict()
        self.prefix = path_prefix
        if samples_file is not None:
            setattr(self, 'document', self.load_file(samples_file))
            setattr(self, 'challenge_problem', self.load_challenge_problem())
            setattr(self, 'experiment_id', self.load_experiment_id())
            setattr(self, 'experiment_design', self.load_experiment_design())
            setattr(self, '_samples', self.load_samples())

    @classmethod
    def init_stores(cls, mongodb_settings):
        # Assemble dict of stores keyed):
        stores = dict()
        for pkg in tuple(jsonschemas.schemas.STORE_SCHEMAS):
            try:
                m = dynamic_import('.' + pkg, package='datacatalog')
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

    def load_challenge_problem(self):
        doc_value = self.document.get('challenge_problem', 'UNKNOWN')
        challenge_problem = self.get('challenge_problem', 'id', doc_value)
        return challenge_problem

    def load_experiment_id(self):
        doc_value = self.document.get('experiment_id', 'UNKNOWN')
        # experiment_id = self.get('experiment', 'experiment_id', doc_value)
        return doc_value

    def load_experiment_design(self):
        doc_value = self.document.get('experiment_reference', 'UNKNOWN')
        experiment_design = self.get('experiment_design', 'experiment_design_id', doc_value)
        return experiment_design

    def load_samples(self):
        samples_list = self.document.get('samples', [])
        return samples_list

    def _update_param(self, strategy):
        """Shim in case we need to validate or add new strategy to BaseStore"""
        return strategy

    def process_experiment(self, parent_uuid=None, strategy='merge'):
        try:
            # For now, this is a dummy experimental record
            expt_doc = {'experiment_id': self.experiment_id}
            if 'child_of' in expt_doc:
                expt_doc['child_of'].append(parent_uuid)
            else:
                expt_doc['child_of'] = [parent_uuid]
            # For now, ALWAYS replace lab-specific experiment record
            resp = self.stores['experiment'].add_update_document(
                expt_doc, strategy=self._update_param('replace'))

            parent_uuid = resp['uuid']
            self.process_samples(parent_uuid=parent_uuid,
                                 strategy=self._update_param(strategy))
            return True
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process experiment', exc)

    def process_samples(self, parent_uuid=None, strategy='merge'):
        try:
            for sample in self._samples:
                if 'child_of' in sample:
                    sample['child_of'].append(parent_uuid)
                else:
                    sample['child_of'] = [parent_uuid]
                if 'measurements' in sample:
                    measurements = sample.pop('measurements')
                else:
                    measurements = None
                resp = self.stores['sample'].add_update_document(sample, strategy=self._update_param(strategy))
                parent_uuid = resp['uuid']
                if 'measurements' is not None:
                    self.process_measurements(measurements, parent_uuid, strategy=self._update_param(strategy))
            return True
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process sample(s)', exc)

    def process_measurements(self, measurements, parent_uuid=None, strategy='merge'):
        try:
            for meas in measurements:
                if 'child_of' in meas:
                    meas['child_of'].append(parent_uuid)
                else:
                    meas['child_of'] = [parent_uuid]
                if 'files' in meas:
                    files = meas.pop('files')
                else:
                    files = None
                resp = self.stores['measurement'].add_update_document(meas, strategy=self._update_param(strategy))
                parent_uuid = resp['uuid']
                if 'files' is not None:
                    self.process_files(files, parent_uuid, strategy=self._update_param(strategy))
            return True
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process measurement(s)', exc)

    def process_files(self, files, parent_uuid=None, strategy='merge'):
        try:
            for file in files:
                file['name'] = self.contextualize(file['name'])
                if 'child_of' in file:
                    file['child_of'].append(parent_uuid)
                else:
                    file['child_of'] = [parent_uuid]
                self.stores['file'].add_update_document(file, strategy=self._update_param(strategy))
            return True
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process file(s)', exc)

    def contextualize(self, filename):
        if filename.startswith('/'):
            filename = filename[1:]
        return os.path.join(self.prefix, filename)

    def process(self, strategy='merge'):
        """Recursiveley loads contents of a sample set into the catalog

        Args:
            replace (bool, optional): Replace existing records. Default is to merge.

        Returns:
            bool: Returns `True` on success
        """
        # HACK Avoid RecursionError('maximum recursion depth exceeded in comparison',)
        sys.setrecursionlimit(10000)
        try:
            expt_design_uuid = getattr(self, 'experiment_design').get('uuid')
            return self.process_experiment(parent_uuid=expt_design_uuid, strategy=strategy)
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process file', exc)
