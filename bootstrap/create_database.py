"""Create database
"""
import argparse
import copy
import json
import logging
import os
import sys
import tempfile
from pprint import pprint
from pymongo import CursorType, MongoClient
from pymongo.errors import OperationFailure
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
logger = logging.getLogger(__name__)

def main(args):

    logger.debug('Project config: ' + PARENT + '/config.yml')
    project_settings = config.read_config(places_list=[PARENT])
    logger.debug('Local config:' + THIS + '/config.yml')
    bootstrap_settings = config.read_config(places_list=[THIS])
    settings = datacatalog.dicthelpers.data_merge(
        project_settings, bootstrap_settings)

    # mongodb = project_settings.get('mongodb')
    # mongodb_uri = datacatalog.mongo.get_mongo_uri(mongodb)
    # myclient = MongoClient(mongodb_uri)

    env = args.environment
    if env is None:
        env = 'localhost'
    if args.verbose is True:
        settings['verbose'] = True
    else:
        settings['verbose'] = False

    mongodb = settings.get(env).get('mongodb')
    mongodb_root = {'host': mongodb['host'],
                    'port': mongodb['port'],
                    'username': 'root',
                    'password': mongodb['root_password']}
    mongodb_uri = datacatalog.mongo.get_mongo_uri(mongodb_root)
    logger.debug('MongoDB: {}'.format(mongodb_uri))
    myclient = MongoClient(mongodb_uri)
    database_name = mongodb.get('database', args.database)

    if database_name is not None:
        logger.info('Ensuring existing of {}'.format(database_name))
        myclient[database_name]
        myclient[database_name]['_keep'].insert_one({'note': 'database provisioned'})
        roles = [{'role': 'dbOwner', 'db': database_name}]
        try:
            myclient['admin'].command("createUser", mongodb['username'], pwd=mongodb['password'], roles=roles)
        except OperationFailure:
            myclient['admin'].command("updateUser", mongodb['username'], pwd=mongodb['password'], roles=roles)
        except Exception as opf:
            logger.warning(opf)
        try:
            myclient[database_name].command("createUser", mongodb['username'], pwd=mongodb['password'], roles=roles)
        except OperationFailure:
            myclient[database_name].command("updateUser", mongodb['username'], pwd=mongodb['password'], roles=roles)
        except Exception as opf:
            logger.warning(opf)
        # except OperationFailure:
        #     pass
    else:
        raise Exception('Failed to find database name in config or command line options')

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    loghandler = logging.StreamHandler()
    loghandler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(loghandler)
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help='verbose output', action='store_true', dest='verbose')
    parser.add_argument("-database", help="Database name")
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
