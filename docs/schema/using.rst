.. _schema_using:

================
Using the Schema
================

Validate a JSON Document
------------------------

Here's an demonstration script written in Python3 to validate a local JSON file
against either a local JSON schema file or a schema URI.

.. code-block:: python

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

    SELF = __file__
    CWD = os.getcwd()
    HERE = os.path.dirname(os.path.abspath(__file__))
    THIS = os.path.dirname(SELF)

    JSONSCHEMA_BASE_URL = 'https://schema.catalog.sd2e.org/schemas/'

    logger = logging.getLogger(__name__)

    def resolver(base_uri=JSONSCHEMA_BASE_URL, schema='sample_set'):
        remote_uri = base_uri + schema + '.json'
        print('REMOTE_URI', remote_uri)
        return jsonschema.RefResolver('', '').resolve_remote(remote_uri)

    def main(args):

        class formatChecker(jsonschema.FormatChecker):
            def __init__(self):
                jsonschema.FormatChecker.__init__(self)

        logger.info('Validating {}'.format(args.file))
        instance = json.load(open(args.file, 'r'))
        if validators.url(args.schema):
            logger.info('Remote schema: {}'.format(args.schema))
            json_schema = jsonschema.RefResolver('', '').resolve_remote(args.schema)
        else:
            logger.info('Local schema: {}'.format(args.schema))
            json_schema = json.load(open(args.schema, 'r'))

        try:
            jsonschema.validate(instance, json_schema, format_checker=formatChecker())
        except jsonschema.exceptions.ValidationError as verr:
            logger.critical('Validation failed')
            pprint(verr.__dict__)
        except jsonschema.exceptions.RefResolutionError as verr:
            logger.critical('Failed to resolve a JSON schema reference')
            pprint(verr.__dict__)
        finally:
            logger.info('Validation suceeded')

    if __name__ == '__main__':
        logger.setLevel(logging.INFO)
        parser = argparse.ArgumentParser()
        parser.add_argument("file", help="File to validate")
        parser.add_argument("schema", help="JSON schema (file or URI")
        parser.add_argument('-v', help='Verbose output', action='store_true', dest='verbose')
        args = parser.parse_args()
        main(args)

