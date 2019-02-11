import argparse
import json
import os
import sys
import tempfile
from pprint import pprint

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

import datacatalog
from tacconfig import config
from .drivedocs.challenge import ChallengeMapping

def regenerate(args, update_catalog=False, mongodb=None):

    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTPATH = os.path.join(tempfile.mkdtemp(), 'challenge_problem_id.json')
    else:
        DESTPATH = os.path.join(os.getcwd(), 'datacatalog', 'definitions', 'jsondocs', 'challenge_problem_id.json')
        update_catalog = True

    settings = config.read_config()
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
            store.add_update_document(doc)

    return True

def main(args):
    regenerate(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-production', help='manage production deployment', action='store_const',
                        const='production', dest='environment')
    parser.add_argument('-staging', help='manage staging deployment', action='store_const',
                        const='staging', dest='environment')
    parser.add_argument('-development', help='manage development deployment', action='store_const',
                        const='development', dest='environment')
    args = parser.parse_args()
    main(args)
