"""Transforms v1 (python-datacatalog 0.1.4) jobs to v2 (python-datacatalog 0.2.0)
"""
import argparse
import copy
import json
import logging
import os
import sys
import tempfile
from pprint import pprint
from pymongo import CursorType
from agavepy.agave import Agave
from tacconfig import config

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

# Use local not installed install of datacatalog
sys.path.insert(0, GPARENT)

import datacatalog
from datacatalog.identifiers import typeduuid, interestinganimal
from datacatalog.dicthelpers import data_merge
from datacatalog.tokens.salt import generate_salt

logging.basicConfig(level=logging.DEBUG)

def main(args):

    def get_v1_items(filter={}):
        """Returns a cursor of v1 items"""
        return v1_stores['pipelinejob'].find(filter=filter)

    def get_v2_items():
        """Returns a cursor of v1 items"""
        v2_stores['pipelinejob'].find(filter)

    settings = config.read_config()
    mongodb_v2 = settings.get('mongodb')
    mongodb_v1 = copy.copy(mongodb_v2)
    # Make overridable

    mongodb_v1['database'] = 'catalog'
    db1 = datacatalog.mongo.db_connection(mongodb_v1)
    v1_stores = dict()
    v1_stores['pipeline'] = db1['pipelines']
    v1_stores['pipelinejob'] = db1['jobs']

    v2_stores = dict()
    v2_stores['pipeline'] = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_v2)
    v2_stores['pipelinejob'] = datacatalog.linkedstores.pipelinejob.PipelineJobStore(mongodb_v2)

    jobs = get_v1_items()
    jc = 0
    logging.info('Jobs found: %s', jobs.count())

    for job in jobs:

        job_doc = dict()
        jc = jc + 1
        logging.debug('Processing job %s', jc)
        # Lift over UUID
        try:
            ouuid = str(job['uuid'])
            nuuid = typeduuid.catalog_uuid_from_v1_uuid(ouuid, uuid_type='pipelinejob')
        except Exception:
            logging.critical('Unable to translate %s. Skipping.', ouuid)
            continue

        try:
            opuuid = str(job['pipeline_uuid'])
            npuuid = typeduuid.catalog_uuid_from_v1_uuid(opuuid, uuid_type='pipeline')
        except Exception:
            logging.critical('Unable to translate %s. Skipping.', opuuid)
            continue

        logging.info('UUID %s remapped to %s', ouuid, nuuid)

        job_doc['uuid'] = nuuid
        job_doc['archive_path'] = os.path.join('/', job['path'])
        job_doc['archive_system'] = 'data-sd2e-community'
        job_doc['session'] = job.get('session',
                                     interestinganimal.generate(
                                         timestamp=False))
        job_doc['updated'] = job.get('updated')
        job_doc['state'] = job.get('status', 'CREATED')
        job_doc['last_event'] = job.get('last_event', 'update').lower()
        job_doc['pipeline_uuid'] = npuuid
        # Linkages
        job_doc['generated_by'] = [npuuid]
        job_doc['child_of'] = list()
        job_doc['derived_from'] = list()

        # Agent/task
        if 'actor_id' in job:
            job_doc['agent'] = 'https://api.sd2e.org/actors/v2/' + job.get('actor_id')
        else:
            job_doc['agent'] = 'https://api.sd2e.org/actors/v2/MEzqaw4rkWZoK'
        job_doc['task'] = None

        # Lift over top-level data
        old_data = job.get('data', dict())
        new_data = dict()

        # Lift over parameters
        # Also establish derived_from params
        for oldkey, newkey, uuid_type in [
            ('sample_id', 'sample_id', 'sample'),
            ('experiment_reference', 'experiment_design_id', 'experiment'),
                ('measurement_id', 'measurement_id', 'measurement')]:
            old_data_filtered = copy.deepcopy(old_data)
            if oldkey in old_data:
                new_data[newkey] = old_data[oldkey]
                old_data_filtered.pop(oldkey)
                value_uuid = typeduuid.catalog_uuid(
                    old_data[oldkey], uuid_type=uuid_type)
                job_doc['derived_from'].append(value_uuid)

        # Merge lifted data and other data fields
        new_data = data_merge(old_data_filtered, new_data)
        if new_data is None:
            new_data = dict()
        job_doc['data'] = new_data

        # Port job history
        v2_history = list()
        for v1_event in job.get('history', []):
            v2_name = list(v1_event.keys())[0]
            v2_event = {'date': v1_event.get(v2_name).get('date'),
                        'data': v1_event.get(v2_name, {}).get('data', dict()),
                        'name': v2_name.lower(),
                        'uuid': typeduuid.generate(
                            uuid_type='pipelinejob_event',
                            binary=False)}
            if v2_event['data'] is None:
                v2_event['data'] = dict()
            v2_history.append(v2_event)
        v2_history = sorted(v2_history, key=lambda k: k['date'])
        job_doc['history'] = v2_history

        # Set system-managed keys
        job_doc = v2_stores['pipelinejob'].set_private_keys(
            job_doc, source=SELF)

        resp = v2_stores['pipelinejob'].coll.insert_one(job_doc)
        logging.debug('Inserted document {}'.format(
            resp.inserted_id))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--db1", help="Database holding v1 schema documents")
    parser.add_argument("--db2", help="Database holding v2 schema documents")
    args = parser.parse_args()
    main(args)
