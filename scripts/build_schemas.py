import os
import sys
import copy
import json
import jsondiff
import tempfile
import argparse
import logging
from jinja2 import Template
from pprint import pprint
import datacatalog

logger = logging.getLogger(__name__)

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)

INDEX_FILENAME = 'schemas.html'
INDEX = '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Schemas</title>
</head>
<body>
    <ul id="navigation">
    {% for item in navigation %}
        <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
    {% endfor %}
    </ul>
</body>
</html>
'''


def load_schema_string(schema_string):
    """Load a schema into a dict from a string

    Args:
        schema_string (str): JSON schema in string format

    Returns:
        dict: JSONschema in ``dict`` form
    """
    try:
        schema = json.loads(schema_string)
        return schema
    except Exception:
        logger.warning('Unable to load schema from string')
        return dict()

def load_schema_file(schema_fname):
    """Load a schema into a dict from a file

    Args:
        schema_fname (str): Relative path to a schema file

    Returns:
        dict: JSONschema in ``dict`` form
    """
    try:
        j = open(schema_fname, 'r')
        schema = json.load(j)
        return schema
    except Exception:
        logger.warning('Unable to load %s from disk', schema_fname)
        return dict()

def compare_schemas(old, new):
    """Compare two schemas for differences, ignoring comments

    Args:
        old (dict): JSONschema in ``dict`` form
        new (dict): JSONschema in ``dict`` form

    Returns:
        bool: Whether the schemas differ materially
    """
    old1 = copy.deepcopy(old)
    new1 = copy.deepcopy(new)

    try:
        del old1['$comment']
    except KeyError:
        pass
    try:
        del new1['$comment']
    except KeyError:
        pass

    diff = jsondiff.diff(old1, new1, marshal=True)
    diff_json = json.dumps(diff, separators=(',', ':'))
    if len(list(diff.keys())) > 0:
        logger.info('Differences found: {}'.format(diff_json))
        return True
    else:
        return False

def regenerate(filters=None):

    template = Template(INDEX)
    elements = list()

    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTDIR = tempfile.mkdtemp()
    else:
        DESTDIR = os.path.join(PARENT, 'schemas')

    for fname, schema in datacatalog.jsonschemas.get_all_schemas(filters).items():
        destpath = os.path.join(DESTDIR, fname + '.json')

        logger.info('Regenerating %s', fname)

        if os.environ.get('MAKETESTS', None) is None:
            if compare_schemas(
                    load_schema_file(destpath), load_schema_string(schema)):
                with open(destpath, 'w+') as j:
                    j.write(schema)
            else:
                logger.debug('%s did not change', fname + '.json')
        else:
            with open(destpath, 'w+') as j:
                j.write(schema)

        # Populate the index file even if the schema was not updated
        # TODO - Display the title and comment from each schema
        elements.append({'href': fname + '.json', 'caption': fname + '.json'})

    logger.info('Building index %s', INDEX_FILENAME)
    elements = sorted(elements, key=lambda k: k['caption'])
    template.render(navigation=elements)
    idxdestpath = os.path.join(DESTDIR, INDEX_FILENAME)
    with open(idxdestpath, 'w+') as i:
        i.write(template.render(navigation=elements))

    return True

def main():

    logger.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", help="Comma-separated list of JSONschema packages")
    args = parser.parse_args()
    if args.filter:
        filters = args.filter.split(',')
    else:
        filters = None
    regenerate(filters)

if __name__ == '__main__':
    main()
