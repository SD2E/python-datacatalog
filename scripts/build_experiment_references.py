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
except ModuleNotFoundError:
    from .exptref import ExperimentReferenceMapping

def regenerate(update_catalog=False, mongodb=None):

    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTPATH = os.path.join(tempfile.mkdtemp(), 'experiment_reference.json')
    else:
        DESTPATH = os.path.join(GPARENT, 'datacatalog', 'definitions', 'jsondocs', 'experiment_reference.json')

    settings = config.read_config()

    mapping = ExperimentReferenceMapping(settings['experiment_reference'], settings['google_client'])
    mapping.populate()
    # Experiment records: Insert into experiment_reference collection
    # FIXME - We don't know which challenge_problem they are children of
    # pprint(mapping.filescache)
    schemadef = mapping.populate().generate_schema_definitions()
    json.dump(schemadef, open(DESTPATH, 'w'), indent=2)

    if update_catalog:
        if mongodb is None:
            mongodb = settings.get('mongodb')
        store = datacatalog.linkedstores.experiment.ExperimentStore(mongodb)
        for doc in mapping.filescache:
            store.add_update_document(doc)

    return True

def main():
    regenerate()

if __name__ == '__main__':
    main()
