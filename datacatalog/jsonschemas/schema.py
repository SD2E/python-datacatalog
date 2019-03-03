import arrow
import json
from os import environ
from datacatalog import settings
from ..utils import camel_to_snake
from .objects import get_class_object

class JSONSchemaBaseObject(object):
    """Interface to JSON schema plus datacatalog-specific extensions"""
    COLLECTION = 'generic'
    BASEREF = settings.SCHEMA_BASEURL
    BASESCHEMA = settings.SCHEMA_REFERENCE
    INDENT = 4
    SORT_KEYS = True
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
        """Dynamically builds ``schema.$id``

        Transforms ``self._filename`` into a schema.id URL in
        the current namespace.
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
        """Dynamically populate ``schema.$comment``

        Combines existing comment with date, rep URL, and git commit hash
        """
        if settings.SCHEMA_NO_COMMENT is False:
            # Dynamically loade since it's expensive to check for git
            from ..githelpers import get_sha1_short, get_remote_uri

            # Create a descriptive $comment for all schema document
            comments = list()
            comments.append('generated: {}'.format(
                arrow.utcnow().format(settings.DATE_FORMAT)))
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
        """Render the schema as a ``dict``

        Private keys are filtered.
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
        """Render the schema as a JSON-formatted string
        """
        self.update_comment()
        my_json = json.dumps(self.to_dict(**kwargs),
                             indent=self.INDENT,
                             sort_keys=self.SORT_KEYS)
        return my_json

    def get_class(self, classname=None):
        return get_class_object(self.to_dict(), classname=classname)

