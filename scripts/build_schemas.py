import os
import sys
import tempfile

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)
sys.path.append(PARENT)
import datacatalog

def regenerate():
    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTDIR = tempfile.mkdtemp()
    else:
        DESTDIR = os.path.join(PARENT, 'schemas')

    for fname, schema in datacatalog.jsonschemas.get_all_schemas().items():
        destpath = os.path.join(DESTDIR, fname + '.json')
        with open(destpath, 'w+') as j:
            j.write(schema)
    return True

def main():
    regenerate()

if __name__ == '__main__':
    main()
