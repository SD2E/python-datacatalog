import argparse
import json
import logging
import os
import sys
import tempfile
from pprint import pprint
from tacconfig import config

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

# Use local not installed install of datacatalog
if GPARENT not in sys.path:
    sys.path.insert(0, GPARENT)
import datacatalog
from .drivedocs.challenge import ChallengeMapping

logger = logging.getLogger(os.path.basename(SELF))
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler()
loghandler.setFormatter(logging.Formatter('%(name)s.%(levelname)s: %(message)s'))
logger.addHandler(loghandler)

def regenerate(args, update_catalog=False, mongodb=None):

    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTPATH = os.path.join(tempfile.mkdtemp(), 'challenge_problem_id.json')
    else:
        DESTPATH = os.path.join(os.getcwd(), 'datacatalog', 'definitions', 'jsondocs', 'challenge_problem_id.json')
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

    mapping = ChallengeMapping(settings['experiment_reference'], settings['google_client'])
    mapping.populate()

    # # Experiment records: Insert into experiment_reference collection
    # # FIXME - We don't know which challenge_problem they are children of
    schemadef = mapping.populate().generate_schema_definitions()
    json.dump(schemadef, open(DESTPATH, 'w'), indent=2)

    if update_catalog:
        if mongodb is None:
            mongodb = db['mongodb']
        store = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb)
        for doc in mapping.filescache:
            logger.info('SYNCING {}'.format(doc.get('title', None)))
            store.add_update_document(doc)

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
