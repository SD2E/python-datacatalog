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

def main(args):

    logging.debug('Reading project config')
    project_settings = config.read_config()
    logging.debug('Reading bootstrap config from ' + THIS + '/config.yml')
    bootstrap_settings = config.read_config(places_list=[THIS])
    mongodb = project_settings.get('mongodb')
    mongodb_uri = datacatalog.mongo.get_mongo_uri(mongodb)
    myclient = MongoClient(mongodb_uri)

    database_name = None
    if args.database is not None:
        database_name = args.database
    else:
        database_name = bootstrap_settings.get('mongodb', {}).get('database', None)

    if database_name is not None:
        logging.info('Creating {}'.format(database_name))
        myclient[database_name]
    else:
        raise Exception('Database name must either be specified in config.yml or via -database')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-database", help="Database name")
    args = parser.parse_args()
    main(args)
