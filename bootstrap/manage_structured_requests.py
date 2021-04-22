"""Manage structured request definitions
"""
import argparse
import copy
import json
import logging
import os
import sys
import tempfile
import pymongo
import datetime
import re
from pprint import pprint
from pymongo import MongoClient, errors
from agavepy.agave import Agave
from tacconfig import config
from .utils import to_json_abstract, clean_keys

COLLECTION = 'cp-request/input/structured_requests'

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
DATA = os.path.join(THIS, COLLECTION)

# Use local not installed install of datacatalog
sys.path.insert(0, GPARENT)
from datacatalog import identifiers, linkedstores, dicthelpers
from datacatalog import settings as settings_module

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

def autobuild(idb, settings):
    ref_store = linkedstores.structured_request.StructuredRequestStore(idb)
    # build_log = open(os.path.join(THIS, os.path.basename(__file__) + '.log'), 'w')

    ref_urls = set()

    for ref in os.listdir(DATA):
        file_path = os.path.join(DATA, ref)
        if os.path.isdir(file_path):
            print("{} is dir".format(file_path))
            continue
        logger.debug('Loading file {}'.format(ref))
        entities = json.load(open(file_path, 'r'))
        if isinstance(entities, dict):
            refslist = list()
            refslist.append(entities)
            entities = refslist
        for ref in entities:
            ref_abs = to_json_abstract(ref)

            try:
                logger.debug('Registering structured request record {}'.format(ref_abs))
                # Patch parameters that have "." in them from Strateos schema
                # Use "|" as a Mongo-compatible delimeter
                # Mongo uses dot notation for sub-field querying, and will reject
                # documents that contain keys with dots
                if "parameters" in ref:
                    for parameter_item in ref["parameters"]:
                        clean_keys(parameter_item)

                resp = ref_store.add_update_document(ref, strategy='merge')
                # build_log.write('{}\t{}\t{}\t{}\n'.format(
                #     'process', resp['experiment_id'], resp['uuid'], resp['_update_token']))
                logger.info('Registered {}'.format(resp['name']))

                ref_urls.add(ref["experiment_reference_url"])
            except Exception:
                logger.exception('Structured request not written')

    experiment_id_date_regex = ".*(\d{4}-\d{2}-\d{2}).*"

    # find old SRs (due to name migration) and remove
    for ref_url in ref_urls:

        candidates = []

        for sr_document in ref_store.query({ "experiment_reference_url" : ref_url }):
            # check derived_from and eid to make sure we don't pull in child SRs
            eid = sr_document["experiment_id"]
            if len(sr_document["derived_from"]) == 0 and re.search(experiment_id_date_regex, eid) is not None:
                candidates.append(sr_document)

        if len(candidates) > 1:

            logger.debug("Resolving old SRs for reference url: {}".format(ref_url))
            latest = datetime.datetime(2000, 1, 1)
            keep_sr = None

            for candidate in candidates:

                modified_date = sr_document["_properties"]["modified_date"]

                if modified_date > latest:
                    latest = modified_date
                    keep_sr = sr_document

            if keep_sr is not None:
                logger.debug("Keeping {} {} {} ".format(keep_sr["experiment_id"], keep_sr["name"], keep_sr["_properties"]["modified_date"]))
                for candidate in candidates:
                    if candidate is not keep_sr:
                        logger.debug("Removing {} {} {} ".format(candidate["experiment_id"], candidate["name"], candidate["_properties"]["modified_date"]))
                        ref_store.delete_document(uuid=candidate["uuid"])

def dblist(idb, settings):
    logger.debug('Listing known entities')
    store = linkedstores.structured_request.StructuredRequestStore(idb)
    for rec in store.query({}):
        logger.info('SR: name="{}" uuid={} updated={}'.format(
            rec['name'], rec['uuid'],
            rec['_properties']['modified_date']))

def main(args):

    logger.debug('Project config: ' + PARENT + '/config.yml')
    project_settings = config.read_config(places_list=[PARENT])
    logger.debug('Local config:' + THIS + '/config.yml')
    bootstrap_settings = config.read_config(places_list=[THIS])
    settings = dicthelpers.data_merge(
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
