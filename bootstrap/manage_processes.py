"""Manage Process definitions
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

COLLECTION = 'processes'
HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
DATA = os.path.join(THIS, COLLECTION)

# Use local not installed install of datacatalog
if GPARENT not in sys.path:
    sys.path.insert(0, GPARENT)
import datacatalog

logger = logging.getLogger(os.path.basename(SELF))
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

def autobuild(idb, settings):
    ref_store = datacatalog.linkedstores.process.ProcessStore(idb)
    build_log = open(os.path.join(THIS, os.path.basename(__file__) + '.log'), 'w')
    for ref in os.listdir(DATA):
        logger.debug('Loading file {}'.format(ref))
        processes = json.load(open(os.path.join(DATA, ref), 'r'))
        if isinstance(processes, dict):
            refslist = list()
            refslist.append(processes)
            processes = refslist
        for ref in processes:
            ref_abs = to_json_abstract(ref)

            try:
                logger.debug('Registering Process record {}'.format(ref_abs))
                resp = ref_store.add_update_document(ref, strategy='merge')
                build_log.write('{}\t{}\t{}\t{}\n'.format(
                    'process', resp['process_id'], resp['uuid'], resp['_update_token']))
                logger.info('Registered {}'.format(resp['name']))
            except Exception:
                logger.exception('Process not added or updated')

def dblist(idb, settings):
    logger.debug('Listing known Processe entities')
    store = datacatalog.linkedstores.process.ReferenceStore(idb)
    for pipe in store.query({}):
        logger.info('Process: id={} name="{}" uuid={} updated={}'.format(
            pipe['process_id'], pipe['name'], pipe['uuid'],
            pipe['_properties']['modified_date']))

def main(args):

    logger.debug('Project config: ' + PARENT + '/config.yml')
    project_settings = config.read_config(places_list=[PARENT])
    logger.debug('Local config:' + THIS + '/config.yml')
    bootstrap_settings = config.read_config(places_list=[THIS])
    settings = datacatalog.dicthelpers.data_merge(
        project_settings, bootstrap_settings)

    env = args.environment
    if env is None:
        env = 'localhost'

    if args.verbose is True:
        settings['verbose'] = True
    else:
        settings['verbose'] = False

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
    parser.add_argument('-localhost', help='manage localhost deployment', action='store_const',
                        const='localhost', dest='environment')
    args = parser.parse_args()
    main(args)
