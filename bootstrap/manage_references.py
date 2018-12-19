"""Manage Reference definitions
"""
import argparse
import copy
import json
import logging
import os
import sys
import tempfile
import pymongo
from pprint import pprint
from pymongo import MongoClient, errors
from agavepy.agave import Agave
from tacconfig import config

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
DATA = os.path.join(THIS, 'references')

# Use local not installed install of datacatalog
sys.path.insert(0, GPARENT)

import datacatalog
logger = logging.getLogger(__name__)

def autobuild(idb, settings):
    store = datacatalog.linkedstores.reference.ReferenceStore(idb)
    build_log = open(os.path.join(THIS, os.path.basename(__file__) + '.log'), 'w')
    for ref in os.listdir(DATA):
        logger.debug('Loading {}'.format(ref))
        reference = json.load(open(os.path.join(DATA, ref), 'r'))
        try:
            resp = store.add_update_document(reference, strategy='drop')
            build_log.write('{}\t{}\t{}\t{}\n'.format(
                resp['reference_id'], resp['name'], resp['uuid'], resp['_update_token']))
            logger.info('Registered {}'.format(resp['name']))
        except Exception:
            logger.warning('Reference not added or updated')

def dblist(idb, settings):
    logger.debug('Listing known references')
    store = datacatalog.linkedstores.reference.ReferenceStore(idb)
    for pipe in store.query({}):
        logger.info('Reference: id={} name="{}" uuid={} updated={}'.format(
            pipe['reference_id'], pipe['name'], pipe['uuid'],
            pipe['_properties']['modified_date']))

def main(args):

    logger.debug('Reading project config')
    project_settings = config.read_config()
    logger.debug('Reading bootstrap config from ' + THIS + '/config.yml')
    bootstrap_settings = config.read_config(places_list=[THIS])
    settings = datacatalog.dicthelpers.data_merge(
        project_settings, bootstrap_settings)

    env = args.environment
    if env is None:
        env = 'localhost'

    if args.verbose is True:
        settings['verbose'] = True

    mongodb = settings.get(env).get('mongodb')

    if args.command == 'list':
        dblist(mongodb, settings)
    elif args.command == 'auto':
        autobuild(mongodb, settings)
    elif args.command == 'create':
        raise NotImplementedError()
    elif args.command == 'delete':
        raise NotImplementedError()

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help="command", choices=['auto', 'list', 'create', 'delete'])
    parser.add_argument('-v', help='verbose output', action='store_true', dest='verbose')
    parser.add_argument('-database', help='override database name')
    parser.add_argument('-production', help='manage production deployment', action='store_const',
                        const='production', dest='environment')
    parser.add_argument('-staging', help='manage staging deployment', action='store_const',
                        const='staging', dest='environment')
    args = parser.parse_args()
    main(args)
