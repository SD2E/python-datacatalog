"""Manage Pipeline definitions
"""
import argparse
import copy
import json
import logging
import os
import sys
import tempfile
from pprint import pprint
from pymongo import MongoClient, errors
from agavepy.agave import Agave
from tacconfig import config

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
DATA = os.path.join(THIS, 'pipelines')

# Use local not installed install of datacatalog
sys.path.insert(0, GPARENT)

import datacatalog

def autobuild(idb, settings):
    store = datacatalog.linkedstores.pipeline.PipelineStore(idb)
    build_log = open(os.path.join(THIS, os.path.basename(__file__) + '.log'), 'w')
    for pipefile in os.listdir(DATA):
        logging.debug('Loading {}'.format(pipefile))
        pipeline = json.load(open(os.path.join(DATA, pipefile), 'r'))
        resp = store.add_update_document(pipeline)
        build_log.write('{}\t{}\t{}\t{}\n'.format(
            resp['id'], resp['name'], resp['uuid'], resp['_update_token']))
        logging.info('Registered {}'.format(resp['name']))

def dblist(idb, settings):
    logging.debug('Listing known pipelines')
    store = datacatalog.linkedstores.pipeline.PipelineStore(idb)
    for pipe in store.query({}):
        logging.info('Pipeline: id={} name="{}" uuid={} updated={}'.format(
            pipe['id'], pipe['name'], pipe['uuid'],
            pipe['_properties']['modified_date']))

def main(args):

    logging.debug('Reading project config')
    project_settings = config.read_config()
    logging.debug('Reading bootstrap config from ' + THIS + '/config.yml')
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
    logging.basicConfig(level=logging.DEBUG)
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
