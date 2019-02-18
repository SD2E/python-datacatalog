"""Transforms v1 (python-datacatalog 0.1.4) pipelines to v2 (python-datacatalog 0.2.0)
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

from .common import safen

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
logger = logging.getLogger(__name__)

def main(args):

    logger.setLevel(logging.DEBUG)

       def get_v1_items(filter={}):
            """Returns a cursor of v1 items"""
            return v1_stores['pipeline'].find(filter=filter)

        def get_v2_items():
            """Returns a cursor of v1 items"""
            v2_stores['pipeline'].find(filter)

        settings = config.read_config()
        mongodb_v2 = settings.get('mongodb')
        mongodb_v1 = copy.copy(mongodb_v2)
        # Make overridable

        mongodb_v1['database'] = 'catalog'
        db1 = datacatalog.mongo.db_connection(mongodb_v1)
        v1_stores = dict()
        v1_stores['pipeline'] = db1['pipelines']

        v2_stores = dict()
        v2_stores['pipeline'] = datacatalog.linkedstores.pipeline.PipelineStore(mongodb_v2)

        logger.debug('Processing pipeline %s', args.uuid1)

        # Lift over UUID
        try:
            opuuid = str(args.uuid1)
            npuuid = typeduuid.catalog_uuid_from_v1_uuid(opuuid, uuid_type='pipeline')
        except Exception:
            logger.critical('Unable to translate %s. Skipping.', opuuid)
            raise

        # Fetch pipeline reference
        v1_pipeline = v1_stores['pipeline'].find_one({'_uuid': args.uuid1})
        if v1_pipeline is None:
            raise ValueError(
                'No such job {} found in v0.1.4 database'.format(args.uuid1))

        # Don't overwrite previously migrated jobs
        if v2_stores['pipeline'].coll.find_one({'uuid': npuuid}) is not None:
            logger.critical('Destination pipeline exists. Skipping.')
            sys.exit(0)

        v2_pipeline = dict()
        v2_pipeline['uuid'] = npuuid

        for key in ('accepts', 'name', 'description', 'components', 'produces',
                    'collections_levels', 'processing_levels'):
            v2_pipeline[key] = v1_pipeline.get(key)

        if args.type is not None:
            v2_pipeline['pipeline_type'] = args.type
        else:
            v2_pipeline['pipeline_type'] = 'primary-etl'
        if args.id is not None:
            v2_pipeline['id'] = args.id
        else:
            v2_pipeline['id'] = safen.encode_title(v2_pipeline['description'])
            logger.debug('Created pipeline.id {}'.format(v2_pipeline['id']))

        # Set managed keys
        v2_pipeline = v2_stores['pipeline'].set_private_keys(
            v2_pipeline, source=SELF)

        if args.verbose:
            pprint(v2_pipeline)

        resp = v2_stores['pipeline'].coll.insert_one(v2_pipeline)
        logger.info('Inserted pipeline document {}'.format(
            resp.inserted_id))

        sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--db1", help="v0.1.4 MongoDB database")
    parser.add_argument("--db2", help="v0.2.0 MongoDB database")
    parser.add_argument("--uuid1", help="Pipeline v1 UUID")
    parser.add_argument("--id", help="Pipeline v2 ID")
    parser.add_argument("--type", help="Pipeine v2 type")
    parser.add_argument("-v",
                        help="Verbose output",
                        action='store_true',
                        dest='verbose')
    args = parser.parse_args()
    main(args)
