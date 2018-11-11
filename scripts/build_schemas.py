import os
import sys
import tempfile
import argparse

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
sys.path.append(PARENT)
import datacatalog

def regenerate(filters=None):
    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTDIR = tempfile.mkdtemp()
    else:
        DESTDIR = os.path.join(PARENT, 'schemas')

    for fname, schema in datacatalog.jsonschemas.get_all_schemas(filters).items():
        destpath = os.path.join(DESTDIR, fname + '.json')
        with open(destpath, 'w+') as j:
            j.write(schema)
    return True

def main():
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
