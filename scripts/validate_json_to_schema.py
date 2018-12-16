import argparse
import json
import jsonschema
import os
import logging
import pytest
import sys
import yaml
import validators

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

from datacatalog.jsonschemas.schema import BASE_URL as JSONSCHEMA_BASE_URL

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, 'data/sampleset')

def resolver(base_uri=JSONSCHEMA_BASE_URL, schema='sample_set'):
    remote_uri = base_uri + schema + '.json'
    print('REMOTE_URI', remote_uri)
    return jsonschema.RefResolver('', '').resolve_remote(remote_uri)

def main(args):

    class formatChecker(jsonschema.FormatChecker):
        def __init__(self):
            jsonschema.FormatChecker.__init__(self)

    logging.info('Validating {}'.format(args.file))
    instance = json.load(open(args.file, 'r'))
    if validators.url(args.schema):
        logging.info('Remote schema: {}'.format(args.schema))
        json_schema = jsonschema.RefResolver('', '').resolve_remote(args.schema)
    else:
        logging.info('Local schema: {}'.format(args.schema))
        json_schema = json.load(open(args.schema, 'r'))

    try:
        jsonschema.validate(instance, json_schema, format_checker=formatChecker())
    except jsonschema.exceptions.ValidationError as verr:
        logging.critical('Validation failed')
        pprint(verr.__dict__)
    except jsonschema.exceptions.RefResolutionError as verr:
        logging.critical('Failed to resolve a JSON schema reference')
        pprint(verr.__dict__)
    finally:
        logging.info('Validation suceeded')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File to validate")
    parser.add_argument("schema", help="JSON schema (file or URI")
    parser.add_argument('-v', help='Verbose output', action='store_true', dest='verbose')
    args = parser.parse_args()
    main(args)
