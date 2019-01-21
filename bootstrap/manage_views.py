"""Manage MongoDB views from code
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

# Use local not installed install of datacatalog
sys.path.insert(0, GPARENT)

import datacatalog
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

def autobuild(idb, settings):
    views = datacatalog.views.aggregations.get_aggregations()
    for viewname, aggregation in views.items():

        try:
            resp = datacatalog.mongo.manage_views.dropView(idb, viewname)
        except Exception as exc:
            logger.warning(exc)

        try:
            datacatalog.mongo.manage_views.createView(idb, viewname, aggregation)
            logger.info('Created view.{}'.format(viewname))
        except errors.OperationFailure as err:
            logger.warning(err)

        if settings['verbose']:
            try:
                built_pipe = datacatalog.mongo.manage_views.getView(idb, viewname).get('cursor').get('firstBatch')[0].get('options').get('pipeline')
                print(json.dumps(built_pipe, indent=2))
            except errors.OperationFailure as err:
                logger.warning(err)

def autodiscover(idb, settings):
    views = datacatalog.views.aggregations.get_aggregations()
    for viewname, aggregation in views.items():
        if settings['verbose']:
            pprint(datacatalog.mongo.manage_views.getView(idb, viewname))
        else:
            print(viewname)

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
    mongodb_uri = datacatalog.mongo.get_mongo_uri(mongodb)
    logger.debug('URI: {}'.format(mongodb_uri))
    database_name = None
    if args.database is not None:
        database_name = args.database
    else:
        database_name = settings.get(env).get('mongodb', {}).get('database', None)
    logger.debug('DB: {}'.format(database_name))

    myclient = MongoClient(mongodb_uri)
    idb = myclient[database_name]

    if args.command == 'discover':
        autodiscover(idb, settings)
    elif args.command == 'auto':
        autobuild(idb, settings)
    elif args.command == 'create':
        raise NotImplementedError()
    elif args.command == 'delete':
        raise NotImplementedError()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help="command", choices=['auto', 'discover', 'create', 'delete'])
    parser.add_argument('-v', help='verbose output', action='store_true', dest='verbose')
    parser.add_argument('-database', help='database name')
    parser.add_argument('-production', help='use local database', action='store_const',
                        const='production', dest='environment')
    parser.add_argument('-staging', help='use staging database', action='store_const',
                        const='staging', dest='environment')
    parser.add_argument('-development', help='manage development deployment', action='store_const',
                        const='development', dest='environment')
    args = parser.parse_args()
    main(args)
