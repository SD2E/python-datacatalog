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
from .utils import to_json_abstract

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)
DATA = os.path.join(THIS, 'references')

# Use local not installed install of datacatalog
sys.path.insert(0, GPARENT)

import datacatalog
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

def autobuild(idb, settings):
    ref_store = datacatalog.linkedstores.reference.ReferenceStore(idb)
    file_store = datacatalog.linkedstores.file.FileStore(idb)
    build_log = open(os.path.join(THIS, os.path.basename(__file__) + '.log'), 'w')
    for ref in os.listdir(DATA):
        logger.debug('Loading file {}'.format(ref))
        references = json.load(open(os.path.join(DATA, ref), 'r'))
        if isinstance(references, dict):
            refslist = list()
            refslist.append(references)
            references = refslist
        for ref in references:
            ref_abs = to_json_abstract(ref)
            derived_froms = dict()

            try:
                logger.debug('Registering reference file {}'.format(ref_abs))
                ag_sys, ag_path, ag_file = datacatalog.agavehelpers.from_agave_uri(ref['uri'])
                fname = os.path.join(ag_path, ag_file)
                ftype = datacatalog.filetypes.infer_filetype(ag_file,
                                                             check_exists=False,
                                                             permissive=True)
                fdoc = {'name': fname, 'type': ftype.label, 'level': 'Reference'}
                resp = file_store.add_update_document(fdoc, strategy='merge')
                build_log.write('{}\t{}\t{}\t{}\n'.format(
                    'file', resp['name'], resp['uuid'], resp['_update_token']))
                logger.info('Registered file {}'.format(resp['uuid']))
                derived_froms[ref['uri']] = resp['uuid']
            except Exception:
                logger.exception('Reference file not added or updated')

            try:
                logger.debug('Registering reference record {}'.format(ref_abs))
                # ref['derived_from'] = derived_froms[ref['uri']]
                resp = ref_store.add_update_document(ref, strategy='merge')
                build_log.write('{}\t{}\t{}\t{}\n'.format(
                    'reference', resp['reference_id'], resp['uuid'], resp['_update_token']))
                ref_store.add_link(resp['uuid'], derived_froms[ref['uri']], relation='derived_from')
                build_log.write('{}\t{}\t{}\t{}\n'.format(
                    'linkage', resp['uuid'], derived_froms[ref['uri']], ''))

                logger.info('Registered {}'.format(resp['name']))
            except Exception:
                logger.exception('Reference not added or updated')


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