import os
import json
import tempfile
import logging
from datacatalog import settings as settings_module

logger = logging.getLogger(__name__)

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)

def lab_to_namespaced_identifier():

    logger.info('Building namespaced identifier from lab schema')

    # build off existing definitions
    DESTDIR = os.path.join(PARENT, 'datacatalog/definitions/jsondocs')

    lab_path = os.path.join(DESTDIR, 'lab.json')
    namespaced_identifier_path = os.path.join(DESTDIR, 'namespaced_identifier.json')  

    lab_schema = json.load(open(lab_path, 'r'))
    namespaced_identifier_schema = json.load(open(namespaced_identifier_path, 'r'))

    # build identifiers built off of lowercase lab names
    namespaced_identifier_string = "|".join(lab.lower() for lab in lab_schema['enum'])
    # e.g. marshall|caltech|uw_biofab|transcriptic|ginkgo|emerald|tacc

    namespaced_identifier_schema["pattern"] = "^(name|experiment|sample|measurement|file|reference|product).(" + namespaced_identifier_string + ")."

    with open(namespaced_identifier_path, 'w+') as j:
        j.write(json.dumps(namespaced_identifier_schema, indent=4, sort_keys=True))

def main():

    logger.setLevel(logging.DEBUG)
    lab_to_namespaced_identifier()

if __name__ == '__main__':
    main()
