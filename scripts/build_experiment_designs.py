import copy
import json
import os
import sys
import tempfile
from pprint import pprint

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

sys.path.append(GPARENT)
sys.path.append(PARENT)

import datacatalog
from tacconfig import config

try:
    from exptref import ExperimentReferenceMapping
    from challenge import ChallengeMapping
except ModuleNotFoundError:
    from .exptref import ExperimentReferenceMapping
    from .challenge import ChallengeMapping

def regenerate(update_catalog=False, mongodb=None):

    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTPATH = os.path.join(tempfile.mkdtemp(), 'experiment_reference.json')
    else:
        DESTPATH = os.path.join(GPARENT, 'datacatalog', 'definitions', 'jsondocs', 'experiment_reference.json')
        update_catalog = True

    settings = config.read_config()

    schema = {'description': 'Experiment reference enumeration',
              'type': 'string',
              'enum': []}

    challenges = ChallengeMapping(settings['experiment_reference'], settings['google_client'])
    challenges.populate()
    for cp in challenges.filescache:
        if cp.get('uri', None) is not None:
            google_sheets_id = os.path.basename(cp.get('uri', None))
            cp_uuid = datacatalog.identifiers.typed_uuid.catalog_uuid(cp.get('id'), 'challenge_problem')
            cp_settings = copy.deepcopy(settings['experiment_reference'])
            cp_settings['google_sheets_id'] = google_sheets_id

            # Generate the experiment designs for each CP
            mapping = ExperimentReferenceMapping(cp_settings, settings['google_client'])
            mapping.populate()
            if update_catalog:
                if mongodb is None:
                    mongodb = settings.get('mongodb')
                store = datacatalog.linkedstores.experiment_design.ExperimentDesignStore(mongodb)
                for doc in mapping.filescache:
                    # print(doc)
                    if doc['experiment_design_id'] != 'Unknown':
                        doc['child_of'].append(cp_uuid)
                    store.add_update_document(doc)

            for rec in mapping.filescache:
                if rec['experiment_design_id'] not in schema['enum']:
                    schema['enum'].append(rec['experiment_design_id'])

    json.dump(schema, open(DESTPATH, 'w'), indent=2)
    return True

def main():
    regenerate()

if __name__ == '__main__':
    main()
