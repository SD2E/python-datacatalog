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

logging.basicConfig(level=logging.DEBUG)

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

import datacatalog
from tacconfig import config

from datacatalog.identifiers import typeduuid

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

    pprint(typeduuid.__dict__)
    jobs = get_v1_items()
    jc = 0
    logging.info('Jobs found: %s', jobs.count())
    for job in jobs:
        jc = jc + 1
        logging.debug('Processing job %s', jc)
        # Lift over UUID
        ouuid = str(job['uuid'])
        nuuid = typeduuid.catalog_uuid_from_v1_uuid(ouuid, uuid_type='pipelinejob')
        logging.info('%s => %s', ouuid, nuuid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--db1", help="Database holding v1 schema documents")
    parser.add_argument("--db2", help="Database holding v2 schema documents")
    args = parser.parse_args()
    main(args)
