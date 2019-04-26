import inspect
import json
import os
import sys
from pprint import pprint

from attrdict import AttrDict
from ...linkedstores.basestore import DocumentSchema
from ...dicthelpers import data_merge

__all__ = ['MongoAggregation', 'MongoViewDocument', 'ViewDocumentInterface']

class MongoAggregation(dict):
    """A MongoDB aggregation"""
    def __new__(cls, value):
        return dict.__new__(cls, value)

class MongoViewDocument(DocumentSchema):
    """Defines JSON schema for a specific view"""
    _index = False

    def __init__(self, inheritance=True, **kwargs):

        # self._index = False
        self._aggregation = None
        # Load JSON schema
        schemaj = dict()
        try:
            module_file = inspect.getfile(self.__class__)
            schemafile = os.path.join(os.path.dirname(module_file), 'schema.json')
            schemaj = json.load(open(schemafile, 'r'))
            if inheritance is True:
                parent_module_file = inspect.getfile(self.__class__.__bases__[0])
                parent_schemafile = os.path.join(os.path.dirname(parent_module_file), 'schema.json')
                pschemaj = json.load(open(parent_schemafile, 'r'))
                schemaj = data_merge(pschemaj, schemaj)
        except Exception:
            raise
        params = {**schemaj, **kwargs}
        super(MongoViewDocument, self).__init__(**params)
        self.update_id()
        self._init_aggregation()

    @classmethod
    def is_indexable(cls):
        """Whether the schema should be returned in collections"""
        return getattr(cls, '_index', True)

    def set_indexable(self, indexable):
        setattr(self, '_index', indexable)
        return self

    def _init_aggregation(self):
        aggr = dict()
        try:
            module_file = inspect.getfile(self.__class__)
            aggfile = os.path.join(os.path.dirname(module_file), 'aggregation.json')
            aggr = MongoAggregation(json.load(open(aggfile, 'r')))
            # print('AGGFILE', aggfile)
        except Exception:
            raise
        setattr(self, '_aggregation', aggr)
        # pprint(getattr(self, '_aggregation'))
        return self

    def get_aggregation(self):
        agg = getattr(self, '_aggregation')
        if agg != dict():
            return getattr(self, '_aggregation')
        else:
            raise NotImplementedError(
                '{} does not support discovery of its aggregator'.format(__name__))

    def to_jsonschema(self, **kwargs):
        if self.is_indexable():
            return super().to_jsonschema(**kwargs)
        else:
            raise NotImplementedError(
                '{} does not support discovery of its JSON schema'.format(__name__))

class ViewDocumentInterface(MongoViewDocument):
    """Alias allowing subclasses to be referenced generically"""
    pass
