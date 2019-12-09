import bacanora
import json
import importlib
import inspect
import itertools
import os
import sys
from pprint import pprint

from datacatalog.agavehelpers import from_agave_uri

from ...identifiers.typeduuid import get_uuidtype
from ...utils import dynamic_import
from ..common import Manager
from ...linkedstores.basestore.exceptions import CatalogError
from ... import jsonschemas

class UnknownReference(CatalogError):
    pass

class SampleSetProcessorError(CatalogError):
    pass

class SampleSetProcessor(Manager):
    """Manager class to process and load sample set JSON documents"""

    def __init__(self,
                 mongodb,
                 agave=None,
                 samples_file=None,
                 samples_uri=None,
                 path_prefix='/uploads', *args, **kwargs):
        Manager.__init__(self, mongodb, agave=agave, *args, **kwargs)
        self.prefix = path_prefix
        self.stats = {'samples': {'count': 0, 'elapsed': 0.0},
                      'measurements': {'count': 0, 'elapsed': 0.0},
                      'files': {'count': 0, 'elapsed': 0.0}}
        self.samples_file = samples_file
        self.samples_uri = samples_uri
        # self.setup(samples_file, samples_uri)

    def setup(self, samples_file=None, samples_uri=None):

        self.logger.debug('Initializing SampleSetProcessor')

        samples_file = getattr(self, 'samples_file', samples_file)
        samples_uri = getattr(self, 'samples_uri', samples_uri)

        # Index the URIand get its UUID
        abs_file_path = None
        file_name = None
        samples_file_uuid = None
        system_id = None

        if samples_uri is not None:
            system_id, file_path, file_name = from_agave_uri(samples_uri)
            abs_file_path = os.path.join(file_path, file_name)
            resp = self.stores['file'].index(abs_file_path,
                                             storage_system=system_id)
            samples_file_uuid = resp.get('uuid', None)
        # No samples file was provided, which means we need to download URI
        if samples_file is None:
            bacanora.download(self.client, abs_file_path,
                              system_id=system_id)
            samples_file = file_name
        setattr(self, 'samples_file_uuid', samples_file_uuid)

        # We can now safely Assume the file is accessible for loading
        document = json.load(open(samples_file, 'r'))
        self.logger.debug('Document.size: {} bytes'.format(sys.getsizeof(document)))

        # Challenge Problem
        doc_cp = document.get('challenge_problem', 'UNKNOWN')
        cp = self.get('challenge_problem', 'id', doc_cp)
        setattr(self, 'challenge_problem', cp)
        self.logger.debug('Challenge_problem: {}'.format(cp))

        # Experiment ID
        doc_exp = document.get('experiment_id', 'UNKNOWN')
        setattr(self, 'experiment_id', doc_exp)
        self.logger.debug('Experiment_id: {}'.format(doc_exp))

        # Experiment Design
        doc_exd = document.get('experiment_reference_url', 'UNKNOWN')
        exd = self.get('experiment_design', 'uri', doc_exd)
        setattr(self, 'experiment_design', exd)
        self.logger.debug('experiment_design: {}'.format(exd))

        # Samples
        setattr(self, '_samples', document.get('samples', []))
        self.logger.debug('count.samples: {}'.format(len(self._samples)))

        self.logger.debug('ready ({})'.format(samples_file))
        return self

    def get(self, doctype, identifier, identifier_value):
        query = {identifier: identifier_value}
        resp = self.stores[doctype].find_one_by_id(**query)
        if resp is None:
            raise UnknownReference('Unable to get {}.{}={}'.format(doctype, identifier, identifier_value))
        else:
            return resp

    def _update_param(self, strategy):
        """Shim in case we need to validate or add new strategy to LinkedStore"""
        return strategy

    def process_experiment(self, parent_uuid=None, strategy='merge'):
        try:
            # For now, this is a dummy experimental record
            expt_doc = {
                'experiment_id': self.experiment_id,
                'child_of': [parent_uuid]
            }
            if getattr(self, 'samples_file_uuid', None) is not None:
                expt_doc['derived_from'] = [getattr(self, 'samples_file_uuid')]
            # if 'child_of' in expt_doc:
            #     expt_doc['child_of'].append(parent_uuid)
            # else:
            #     expt_doc['child_of'] = [parent_uuid]
            # For now, ALWAYS replace lab-specific experiment record
            resp = self.stores['experiment'].add_update_document(
                expt_doc, strategy=self._update_param('replace'))
            new_parent_uuid = resp['uuid']
            assert get_uuidtype(new_parent_uuid) == 'experiment', '{} is mistyped'.format(new_parent_uuid)
            self.process_samples(parent_uuid=new_parent_uuid,
                                 strategy=self._update_param(strategy))
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process experiment', exc)

    def process_samples(self, parent_uuid=None, strategy='merge'):
        try:
            # Samples was cached as _samples at init()
            if not isinstance(self._samples, list):
                raise TypeError('"samples" must be a list')
            for sample in self._samples:
                self.logger.debug('processing.sample: {}'.format(sample['sample_id']))
                if getattr(self, 'samples_file_uuid', None) is not None:
                    sample['derived_from'] = [getattr(self, 'samples_file_uuid')]
                if 'child_of' in sample:
                    sample['child_of'].append(parent_uuid)
                else:
                    sample['child_of'] = [parent_uuid]
                # Don't propagate measurements subdocument in sample record.
                # That's what the linkages are for!
                if 'measurements' in sample:
                    measurements = sample.pop('measurements')
                    self.logger.debug('count.measurements: {}'.format(len(measurements)))
                else:
                    measurements = None
                setattr(self, '_measurements', measurements)
                resp = self.stores['sample'].add_update_document(sample, strategy=self._update_param(strategy))
                new_parent_uuid = resp['uuid']
                assert get_uuidtype(new_parent_uuid) == 'sample', '{} is mistyped'.format(new_parent_uuid)
                if self._measurements is not None:
                    self.process_measurements(new_parent_uuid, strategy=self._update_param(strategy))
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process sample(s)', exc)

    def process_measurements(self, parent_uuid=None, strategy='merge'):
        try:
            if not isinstance(self._measurements, list):
                raise TypeError('"measurements" must be a list')
            for meas in self._measurements:
                self.logger.debug('processing.measurement: {}'.format(meas['measurement_id']))
                if getattr(self, 'samples_file_uuid', None) is not None:
                    meas['derived_from'] = [getattr(self, 'samples_file_uuid')]
                if 'child_of' in meas:
                    meas['child_of'].append(parent_uuid)
                else:
                    meas['child_of'] = [parent_uuid]
                if 'files' in meas:
                    files = meas.pop('files')
                    self.logger.debug('count.files: {}'.format(len(files)))
                else:
                    files = None
                setattr(self, '_files', files)
                resp = self.stores['measurement'].add_update_document(meas, strategy=self._update_param(strategy))
                new_parent_uuid = resp['uuid']
                assert get_uuidtype(new_parent_uuid) == 'measurement', '{} is mistyped'.format(new_parent_uuid)
                if self._files is not None:
                    self.process_files(new_parent_uuid, strategy=self._update_param(strategy))
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process measurement(s)', exc)

    def process_files(self, parent_uuid=None, strategy='merge'):
        try:
            if not isinstance(self._files, list):
                raise TypeError('"files" must be a list')
            for ffile in self._files:
                self.logger.debug('processing.file: {}'.format(ffile['file_id']))
                if getattr(self, 'samples_file_uuid', None) is not None:
                    ffile['derived_from'] = [getattr(self, 'samples_file_uuid')]
                ffile['name'] = self.contextualize(ffile['name'])
                if 'child_of' in ffile:
                    ffile['child_of'].append(parent_uuid)
                else:
                    ffile['child_of'] = [parent_uuid]
                self.stores['file'].add_update_document(ffile, strategy=self._update_param(strategy))
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
        # sys.setrecursionlimit(100000)
        try:
            expt_design_uuid = getattr(self, 'experiment_design').get('uuid')
            self.process_experiment(parent_uuid=expt_design_uuid, strategy=strategy)
            return True
        except Exception as exc:
            raise SampleSetProcessorError('Failed to process file', exc)
