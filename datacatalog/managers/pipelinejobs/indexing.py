import re
import json
from enum import Enum

__all__ = ['ArchiveIndexRequest', 'ProductIndexRequest', 'IndexType', 'IndexingError']

class IndexType(str):
    """An indexing type"""
    MEMBERS = ['archive', 'product']

    def __new__(cls, value):
        value = str(value).lower()
        if value not in cls.MEMBERS:
            raise ValueError('{} is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)

    @property
    def patterns_field(self):
        return self + '_patterns'

class ArchiveIndexRequest(object):
    PARAMS = [('patterns', True, 'filters', []),
              ('note', False, 'note', None),
              ('fixity', False, 'fixity', True),
              ('generated_by', False, 'generated_by', []),
              ('level', True, 'level', '1')]

    def __init__(self, **kwargs):
        for param, mandatory, attr, default in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory else kwargs.get(param, default))
                setattr(self, attr, value)
            except KeyError:
                pass

    def to_dict(self):
        me = dict()
        for param, mandatory, attr, default in self.PARAMS:
            me[attr] = getattr(self, attr, None)
        return me

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))

    def __repr__(self):
        return self.__class__.__name__ + ':' + str(self.to_dict())

    def regex(self):
        """Compile the request's filters list into a Python regex
        """
        return re.compile('|'.join(getattr(self, 'filters', [])))

class ProductIndexRequest(object):
    PARAMS = [('patterns', True, 'filters', []),
              ('note', False, 'note', None),
              ('fixity', False, 'fixity', False),
              ('derived_from', False, 'derived_from', []),
              ('derived_using', False, 'derived_using', [])]

    def __init__(self, **kwargs):
        for param, mandatory, attr, default in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory else kwargs.get(param, default))
                setattr(self, attr, value)
            except KeyError:
                pass

    def to_dict(self):
        me = dict()
        for param, mandatory, attr, default in self.PARAMS:
            me[attr] = getattr(self, attr, None)
        return me

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))

    def __repr__(self):
        return self.__class__.__name__ + ':' + str(self.to_dict())

    def regex(self):
        """Compile the request's filters list into a Python regex
        """
        return re.compile('|'.join(getattr(self, 'filters', [])))

class IndexingError(Exception):
    """An error has occurred during setup or execution of an indexing task
    """
    pass
