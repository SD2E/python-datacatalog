import re
import validators

from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.linkedstores.basestore import HeritableDocumentSchema

TYPE_SIGNATURE = ('structured_request', '125', 'Structured Experiment Request')

NAME_MAX_LEN = 256
NAME_REGEX = re.compile('^[a-zA-Z0-9][a-zA-Z0-9-.]{1,62}[a-zA-Z0-9]$')
DESC_MAX_LEN = 256
DESC_REGEX = re.compile('^.{0,256}$')

class StructuredRequestSchema(HeritableDocumentSchema):
    """Defines the Structured Request schema"""

    def __init__(self, inheritance=True, **kwargs):
        super(StructuredRequestSchema, self).__init__(
              inheritance=True,
              document='schema.json',
              filters='filters.json',
              **kwargs)
        self.update_id()

class StructuredRequestDocument(ExtensibleAttrDict):
    """Instantiates an instance of Structured Request"""

    PARAMS = [('name', True, 'name', None),
              ('description', False, 'description', ''),
              ('_visible', False, '_visible', True)]

    def __init__(self, schema=None, **kwargs):
        if schema is None:
            schema = StructuredRequestSchema()
        for attr, req, param, default in self.PARAMS:
            if req is True:
                if attr not in kwargs:
                    raise KeyError('{} is a mandatory field'.format(attr))
            setattr(self, attr, kwargs.get(param, default))

        # Request name length (technically redundant with regex validation)
        if len(self.name) >= NAME_MAX_LEN:
            raise ValueError(
                'Structured request name can have a max of {} characters'.format(
                    NAME_MAX_LEN))
        # Validate name with regex
        if not NAME_REGEX.search(self.name):
            raise ValueError('{} is not a valid structured request name'.format(self.name))
        # Max description length (technically redundant with regex validation)
        if len(self.description) >= DESC_MAX_LEN:
            raise ValueError(
                'Structured request description can have a max of {} characters'.format(
                    DESC_MAX_LEN))
        # Validate description with regex
        if not DESC_REGEX.search(self.description):
            raise ValueError('This is not a valid structured request description')
