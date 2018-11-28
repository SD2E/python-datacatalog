import os
import sys
import tempfile
import argparse
from jinja2 import Template
import datacatalog

HERE = os.getcwd()
THIS = os.path.dirname(__file__)
PARENT = os.path.dirname(THIS)

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

def regenerate(filters=None):

    template = Template(INDEX)
    elements = list()

    if datacatalog.config.get_osenv_bool('MAKETESTS'):
        DESTDIR = tempfile.mkdtemp()
    else:
        DESTDIR = os.path.join(PARENT, 'schemas')

    for fname, schema in datacatalog.jsonschemas.get_all_schemas(filters).items():
        destpath = os.path.join(DESTDIR, fname + '.json')
        with open(destpath, 'w+') as j:
            j.write(schema)
        elements.append({'href': fname + '.json', 'caption': fname + '.json'})

    elements = sorted(elements, key=lambda k: k['caption'])
    template.render(navigation=elements)
    idxdestpath = os.path.join(DESTDIR, 'index.html')
    with open(idxdestpath, 'w+') as i:
        i.write(template.render(navigation=elements))

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
