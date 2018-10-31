import os
import sys
import tempfile

HERE = os.path.dirname(__file__)
PARENT = os.path.dirname(HERE)
sys.path.append(PARENT)
from datacatalog.config import get_osenv_bool
from datacatalog.jsonschemas import get_all_schemas

def regenerate():
    if get_osenv_bool('MAKETESTS'):
        DESTDIR = tempfile.mkdtemp()
    else:
        DESTDIR = os.path.join(PARENT, 'schemas')

    for fname, schema in get_all_schemas().items():
        destpath = os.path.join(DESTDIR, fname + '.json')
        with open(destpath, 'w+') as j:
            j.write(schema)
    return True

def main():
    regenerate()

if __name__ == '__main__':
    main()
