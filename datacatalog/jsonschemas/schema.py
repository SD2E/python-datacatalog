import arrow
import json
import re

import config
from githelpers import get_sha1_short, get_remote_uri

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
INDENT = 4
SORT_KEYS = True

class JSONSchemaBaseObject(object):
    COLLECTION = 'generic'
    BASEREF = 'https://sd2e.github.io/python-datacatalog/schemas/'
    PARAMS = [('schema', False, 'schema', 'http://json-schema.org/draft-07/schema#', '$'),
              ('id', False, 'id', '', '$'),
              ('definitions', False, 'definitions', None, ''),
              ('title', False, 'title', None, ''),
              ('description', False, 'description', None, ''),
              ('additionalProperties', False, 'additionalProperties', False, ''),
              ('type', False, 'type', 'object', ''),
              ('properties', False, 'properties', None, ''),
              ('required', False, 'required', None, ''),
              ('pattern', False, 'pattern', None, ''),
              ('enum', False, 'enum', None, ''),
              ('_filename', False, '_filename', 'baseobject', ''),
              ('_snake_case', False, '_snake_case', True, ''),
              ('_collection', False, '__collection', None, ''),
              ('_indexes', False, '__indexes', None, ''),
              ('_identifiers', False, '__identifiers', None, ''),
              ('_uuid_type', False, '__uuid_type', 'generic', ''),
              ('_uuid_fields', False, '__uuid_fields', 'id', ''),
              ('_visible', False, '_visible', True, ''),
              ('comment', False, 'comment', '', '$')]

    def __init__(self, **kwargs):
        for key, mandatory, param, default, keyfix in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory
                         else kwargs.get(param, default))
            except KeyError:
                raise KeyError(
                    'parameter "{}" is mandatory'.format(param))
            if value is not None:
                setattr(self, key, value)

        if not config.get_osenv_bool('NO_JSONSCHEMA_COMMENT'):

            # Create a descriptive $comment for all schema document
            comments = list()
            comments.append('generated: {}'.format(arrow.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ')))
            try:
                # If we are able to resolve
                short_hash = get_sha1_short()
                remote = get_remote_uri()
                comments.append('source: {}@{}'.format(remote, short_hash))
            except Exception:
                pass
            comment_string = '; '.join(comments)
            setattr(self, 'comment', comment_string)

        self.update_id()

    def update_id(self):
        temp_fname = getattr(self, '_filename')
        if self._snake_case:
            temp_fname = camel_to_snake(temp_fname)
        schema_id = self.BASEREF + temp_fname
        schema_id = schema_id.lower()
        if not schema_id.endswith('.json'):
            schema_id = schema_id + '.json'
        setattr(self, 'id', schema_id)

    def to_dict(self, private_prefix='_', **kwargs):
        my_dict = dict()
        for key, mandatory, param, default, keyfix in self.PARAMS:
            fullkey = keyfix + key
            if not key.startswith(private_prefix) and default is not None:
                my_dict[fullkey] = getattr(self, param, None)
        for key in self.__dict__:
            refkey = '$' + key
            if not key.startswith(private_prefix):
                if refkey not in my_dict:
                    my_dict[key] = getattr(self, key, None)
        return my_dict

    def to_jsonschema(self, **kwargs):
        my_json = json.dumps(self.to_dict(**kwargs), indent=INDENT, sort_keys=SORT_KEYS)
        return my_json

def camel_to_snake(name):
    s1 = FIRST_CAP_RE.sub(r'\1_\2', name)
    return ALL_CAP_RE.sub(r'\1_\2', s1).lower()
