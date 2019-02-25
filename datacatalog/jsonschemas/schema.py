import arrow
import json
import re
from os import environ
from . import config
from .objects import get_class_object

BASE_URL = 'https://schema.catalog.sd2e.org/schemas/'
"""Default base URL against which JSONschema documents are resolved"""
BASE_SCHEMA = 'http://json-schema.org/draft-07/schema#'
"""References in-use JSON schema version"""

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
INDENT = 4
SORT_KEYS = True

class JSONSchemaBaseObject(object):
    """Interface to JSON schema plus datacatalog-specific extensions"""
    COLLECTION = 'generic'
    BASEREF = environ.get('PROJECT_SCHEMA_BASE_URL', BASE_URL)
    BASESCHEMA = environ.get('PROJECT_SCHEMA_REF', BASE_SCHEMA)
    PARAMS = [('schema', False, 'schema', BASESCHEMA, '$'),
              ('comment', False, 'comment', '', '$'),
              ('id', False, 'id', '', '$'),
              ('definitions', False, 'definitions', None, ''),
              ('title', False, 'title', None, ''),
              ('description', False, 'description', None, ''),
              ('additionalProperties', False, 'additionalProperties', False, ''),
              ('type', False, 'type', 'object', ''),
              ('items', False, 'items', None, ''),
              ('oneOf', False, 'oneOf', None, ''),
              ('properties', False, 'properties', None, ''),
              ('required', False, 'required', None, ''),
              ('pattern', False, 'pattern', None, ''),
              ('enum', False, 'enum', None, ''),
              ('format', False, 'format', None, ''),
              ('examples', False, 'examples', None, ''),
              ('_filename', False, '_filename', 'baseobject', ''),
              ('_snake_case', False, '_snake_case', True, ''),
              ('_collection', False, '__collection', None, ''),
              ('_indexes', False, '__indexes', None, ''),
              ('_identifiers', False, '__identifiers', None, ''),
              ('_uuid_type', False, '__uuid_type', 'generic', ''),
              ('_uuid_fields', False, '__uuid_fields', 'id', ''),
              ('_visible', False, '_visible', True, '')]

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

        self.update_id()

    def update_id(self):
        """Build ``schema.$id`` into a valid URI around ``self._filename``
        """
        temp_fname = getattr(self, '_filename')
        if self._snake_case:
            temp_fname = camel_to_snake(temp_fname)
        schema_id = self.BASEREF + temp_fname
        schema_id = schema_id.lower()
        if not schema_id.endswith('.json'):
            schema_id = schema_id + '.json'
        setattr(self, 'id', schema_id)

    def update_comment(self):
        """Create ``schema.$comment`` with date, source URL,
        and git commit hash (if available) on demand.
        """

        if not config.get_osenv_bool('PROJECT_SCHEMA_NO_COMMENT'):

            # Dynamically loade since it's expensive to check for git
            from ..githelpers import get_sha1_short, get_remote_uri

            # Create a descriptive $comment for all schema document
            comments = list()
            comments.append('generated: {}'.format(arrow.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ')))
            try:
                # If we are able to resolve a git reference
                short_hash = get_sha1_short()
                remote = get_remote_uri()
                comments.append('source: {}@{}'.format(remote, short_hash))
            except Exception:
                pass
            comment_string = '; '.join(comments)
            setattr(self, 'comment', comment_string)

    def to_dict(self, private_prefix='_', **kwargs):
        """Express the schema as a ``dict`` filtering private keys
        """
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
        """Express the schema as a JSON-formatted string
        """
        self.update_comment()
        my_json = json.dumps(self.to_dict(**kwargs), indent=INDENT, sort_keys=SORT_KEYS)
        return my_json

    def get_class(self, classname=None):
        return get_class_object(self.to_dict(), classname=classname)

def camel_to_snake(name):
    s1 = FIRST_CAP_RE.sub(r'\1_\2', name)
    return ALL_CAP_RE.sub(r'\1_\2', s1).lower()
