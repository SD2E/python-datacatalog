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

def regenerate(update_catalog=False, mongodb=None):

    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTPATH = os.path.join(tempfile.mkdtemp(), 'challenge_problem_id.json')
    else:
        DESTPATH = os.path.join(os.getcwd(), 'datacatalog', 'definitions', 'jsondocs', 'challenge_problem_id.json')
        update_catalog = True

    settings = config.read_config()
    mapping = ChallengeMapping(settings['experiment_reference'], settings['google_client'])
    mapping.populate()

    # # Experiment records: Insert into experiment_reference collection
    # # FIXME - We don't know which challenge_problem they are children of
    schemadef = mapping.populate().generate_schema_definitions()
    json.dump(schemadef, open(DESTPATH, 'w'), indent=2)

    if update_catalog:
        if mongodb is None:
            mongodb = settings.get('mongodb')
        store = datacatalog.linkedstores.challenge_problem.ChallengeStore(mongodb)
        for doc in mapping.filescache:
            store.add_update_document(doc)

    return True

def main():
    regenerate()

if __name__ == '__main__':
    main()
