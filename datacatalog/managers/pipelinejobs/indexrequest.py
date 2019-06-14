import re
import json
from enum import Enum
from datacatalog.extensible import ExtensibleAttrDict

__all__ = ['ArchiveIndexRequest', 'ProductIndexRequest', 'IndexType',
           'IndexingError', 'InvalidIndexingRequest', 'get_index_request',
           'ARCHIVE', 'PRODUCT']

ARCHIVE = 'archive'
PRODUCT = 'product'

class IndexType(str):
    """An named indexing type"""
    MEMBERS = [ARCHIVE, PRODUCT]
    kind = None

    def __new__(cls, value):
        value = str(value).lower()
        if value not in cls.MEMBERS:
            raise InvalidIndexingRequest('{} is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)

    @property
    def patterns_field(self):
        return self + '_patterns'

class IndexRequest(ExtensibleAttrDict):
    PARAMS = None
    kind = None

    def __init__(self, **kwargs):
        # Transform processing_level to level
        if kwargs.get('processing_level', None) is not None:
            kwargs['level'] = kwargs.get('processing_level', '1')
        if kwargs.get('level', None) is None:
            if kwargs.get('processing_level', None) is not None:
                kwargs['level'] = kwargs.get('processing_level', '1')
        # Transform filters to patterns
        if kwargs.get('patterns', None) is None:
            if kwargs.get('filters', None) is not None:
                kwargs['patterns'] = kwargs.get('filters', [])

        for param, mandatory, attr, default in self.PARAMS:
            try:
                value = kwargs[param] if mandatory else kwargs.get(param, default)
                setattr(self, attr, value)
            except KeyError:
                raise InvalidIndexingRequest('{} missing required key {}'.format(
                    self.__class__.__name__, param))

    def to_dict(self):
        me = dict()
        for param, mandatory, attr, default in self.PARAMS:
            me[attr] = getattr(self, attr, None)
        return me

    @property
    def params(self):
        return self.PARAMS

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))

    def regex(self):
        """Compile the request's filters list into a Python regex
        """
        return re.compile('|'.join(getattr(self, 'filters', [])))

    def __repr__(self):
        return self.__class__.__name__ + ':' + str(self.to_dict())

class ArchiveIndexRequest(IndexRequest):
    PARAMS = [('patterns', True, 'filters', []),
              ('note', False, 'note', None),
              ('fixity', False, 'fixity', True),
              ('generated_by', False, 'generated_by', []),
              ('level', True, 'level', '1')]
    kind = ARCHIVE

class ProductIndexRequest(IndexRequest):
    PARAMS = [('patterns', True, 'filters', []),
              ('note', False, 'note', None),
              ('fixity', False, 'fixity', False),
              ('generated_by', False, 'generated_by', []),
              ('derived_from', True, 'derived_from', []),
              ('derived_using', False, 'derived_using', [])]
    kind = PRODUCT

class IndexingError(Exception):
    """An error has occurred during setup or execution of an indexing task
    """
    pass

class InvalidIndexingRequest(ValueError):
    """An error has occurred during setup or execution of an indexing task
    """
    pass

def get_index_request(**kwargs):
    """Transform an index request dict into a typed IndexRequest object
    """
    try:
        return ArchiveIndexRequest(**kwargs)
    except InvalidIndexingRequest:
        return ProductIndexRequest(**kwargs)
    except Exception:
        raise
