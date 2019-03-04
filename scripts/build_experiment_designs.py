import argparse
import copy
import json
import logging
import os
import sys
import tempfile
from pprint import pprint

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

# Use local not installed install of datacatalog
if GPARENT not in sys.path:
    sys.path.insert(0, GPARENT)
import datacatalog
from tacconfig import config

from .drivedocs.challenge import ChallengeMapping
from .drivedocs.exptref import ExperimentReferenceMapping

logger = logging.getLogger(os.path.basename(SELF))
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

def regenerate(args, update_catalog=False, mongodb=None):

    if datacatalog.settings.parse_boolean(os.environ.get('MAKETESTS')):
        DESTPATH = os.path.join(tempfile.mkdtemp(), 'experiment_reference.json')
    else:
        DESTPATH = os.path.join(os.getcwd(), 'datacatalog', 'definitions', 'jsondocs', 'experiment_reference.json')
        update_catalog = True

    logger.debug('Project config: ' + PARENT + '/config.yml')
    project_settings = config.read_config(places_list=[PARENT])
    logger.debug('Local config:' + THIS + '/config.yml')
    bootstrap_settings = config.read_config(places_list=[THIS])
    settings = datacatalog.dicthelpers.data_merge(
        project_settings, bootstrap_settings)

    env = args.environment
    if env is None:
        env = 'development'
    db = settings.get(env)

    schema = {'description': 'Experiment reference enumeration',
              'type': 'string',
              'enum': []}

    challenges = ChallengeMapping(settings['experiment_reference'], settings['google_client'])
    challenges.populate()
    for cp in challenges.filescache:
        if cp.get('uri', None) is not None:
            google_sheets_id = os.path.basename(cp.get('uri', None))
            cp_uuid = datacatalog.identifiers.typeduuid.catalog_uuid(cp.get('id'), 'challenge_problem')
            cp_settings = copy.deepcopy(settings['experiment_reference'])
            cp_settings['google_sheets_id'] = google_sheets_id

            # Generate the experiment designs for each CP
            mapping = ExperimentReferenceMapping(cp_settings, settings['google_client'])
            mapping.populate()
            if update_catalog:
                if mongodb is None:
                    mongodb = db['mongodb']
                store = datacatalog.linkedstores.experiment_design.ExperimentDesignStore(mongodb)
                for doc in mapping.filescache:
                    # print(doc)
                    if doc['experiment_design_id'] != 'Unknown':
                        doc['child_of'].append(cp_uuid)
                    logger.info('SYNCING {}'.format(doc.get('title', None)))
                    store.add_update_document(doc)

            for rec in mapping.filescache:
                if rec['experiment_design_id'] not in schema['enum']:
                    schema['enum'].append(rec['experiment_design_id'])

    json.dump(schema, open(DESTPATH, 'w'), indent=2)
    return True

def main(args):
    regenerate(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help='verbose output', action='store_true', dest='verbose')
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
