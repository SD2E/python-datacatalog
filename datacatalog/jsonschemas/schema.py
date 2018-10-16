import json
import re

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
INDENT = 2
SORT_KEYS = True

class JSONSchemaBaseObject(object):
    BASEREF = 'https://sd2e.github.io/python-datacatalog/schemas/'
    PARAMS = [('schema', False, '_schema', 'http://json-schema.org/draft-07/schema#', '$'),
              ('additionalProperties', False, 'additionalProperties', False, ''),
              ('type', False, 'type', 'object', ''),
              ('properties', False, 'properties', None, ''),
              ('required', False, 'required', None, ''),
              ('title', False, 'title', None, ''),
              ('description', False, 'description', None, ''),
              ('definitions', False, 'definitions', None, ''),
              ('pattern', False, 'pattern', None, ''),
              ('_filename', False, '_filename', 'BaseObject', ''),
              ('id', False, '_id', '', '$'),
              ('enum', False, 'enum', None, ''),
              ('_snake_case', False, '_snake_case', True, '')]

    def __init__(self, **kwargs):
        for key, mandatory, param, default, keyfix in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory
                         else kwargs.get(param, default))
            except KeyError:
                raise KeyError(
                    'parameter "{}" is mandatory'.format(param))
            if not value is None:
                setattr(self, param, value)
        self.update_id()

    def update_id(self):
        temp_fname = getattr(self, '_filename')
        if self._snake_case:
            temp_fname = camel_to_snake(temp_fname)
        schema_id = self.BASEREF + temp_fname
        schema_id = schema_id.lower()
        if not schema_id.endswith('.json'):
            schema_id = schema_id + '.json'
        setattr(self, '_id', schema_id)

    def to_dict(self, filt='_'):
        my_dict = dict()
        for key, mandatory, param, default, keyfix in self.PARAMS:
            if not key.startswith(filt) and default is not None:
                my_dict[keyfix + key] = getattr(self, param, None)
        for key in self.__dict__:
            if not key.startswith(filt):
                if key not in my_dict:
                    my_dict[key] = getattr(self, key, None)
        return my_dict

    def to_jsonschema(self, **kwargs):
        my_json = json.dumps(self.to_dict(filt='_'), indent=INDENT, sort_keys=SORT_KEYS)
        return my_json

def camel_to_snake(name):
    s1 = FIRST_CAP_RE.sub(r'\1_\2', name)
    return ALL_CAP_RE.sub(r'\1_\2', s1).lower()
