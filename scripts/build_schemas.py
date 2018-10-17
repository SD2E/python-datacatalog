import os
import sys

HERE = os.path.dirname(__file__)
PARENT = os.path.dirname(HERE)
DESTDIR = os.path.join(PARENT, 'schemas')
sys.path.append(PARENT)

from datacatalog.jsonschemas import get_all_schemas

for fname, schema in get_all_schemas().items():
    destpath = os.path.join(DESTDIR, fname + '.json')
    with open(destpath, 'w+') as j:
        j.write(schema)
