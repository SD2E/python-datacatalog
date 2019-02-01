"""Manage additional EXD definitions
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
from .utils import to_json_abstract

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
DATA = os.path.join(THIS, 'experiments')

# Use local not installed install of datacatalog
sys.path.insert(0, GPARENT)

import datacatalog
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

def autobuild(idb, settings):
    ref_store = datacatalog.linkedstores.experiment.ExperimentStore(idb)
    build_log = open(os.path.join(THIS, os.path.basename(__file__) + '.log'), 'w')
    for ref in os.listdir(DATA):
        logger.debug('Loading file {}'.format(ref))
        entities = json.load(open(os.path.join(DATA, ref), 'r'))
        if isinstance(entities, dict):
            refslist = list()
            refslist.append(entities)
            entities = refslist
        for ref in entities:
            ref_abs = to_json_abstract(ref)

            try:
                logger.debug('Registering EXP record {}'.format(ref_abs))
                resp = ref_store.add_update_document(ref, strategy='merge')
                build_log.write('{}\t{}\t{}\t{}\n'.format(
                    'process', resp['experiment_id'], resp['uuid'], resp['_update_token']))
                logger.info('Registered {}'.format(resp['title']))
            except Exception:
                logger.exception('Process not added or updated')

def dblist(idb, settings):
    logger.debug('Listing known entities')
    store = datacatalog.linkedstores.experiment.ExperimentStore(idb)
    for pipe in store.query({}):
        logger.info('EXP: id={} name="{}" uuid={} updated={}'.format(
            pipe['experiment_id'], pipe['title'], pipe['uuid'],
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
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help="command", choices=['auto', 'list', 'create', 'delete'])
    parser.add_argument('-v', help='verbose output', action='store_true', dest='verbose')
    parser.add_argument('-database', help='override database name')
    parser.add_argument('-production', help='manage production deployment', action='store_const',
                        const='production', dest='environment')
    parser.add_argument('-staging', help='manage staging deployment', action='store_const',
                        const='staging', dest='environment')
    parser.add_argument('-development', help='manage development deployment', action='store_const',
                        const='development', dest='environment')
    args = parser.parse_args()
    main(args)