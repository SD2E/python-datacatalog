from datacatalog import linkages 
from jsonmerge import merge, Merger

__all__ = ['APPEND', 'MERGE', 'OVERWRITE', 'DISCARD', 'ALL', 
           'DEFAULT_JSONMERGE_STRATEGY', 'json_merge']

APPEND = 'append'
MERGE = 'arrayMergeById'
OVERWRITE = 'overwrite'
DISCARD = 'discard'

ALL = (APPEND, MERGE, OVERWRITE, DISCARD)
DEFAULT_JSONMERGE_STRATEGY = APPEND

class JSONMergeError(Exception):
    pass

class JSONMergeStrategy(str):
    """A JSON merge strategy"""
    def __new__(cls, value):
        value = str(value).lower()
        if value not in ALL:
            raise JSONMergeError('"{}" is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)

def get_merger(merge_strategy):
    schema = {'properties': {}}
    for lkg in linkages.ALL:
        schema[lkg] = {'mergeStrategy': JSONMergeStrategy(merge_strategy)}
    merger = Merger(schema)
    return merger

def json_merge(a, b, merge_strategy=DEFAULT_JSONMERGE_STRATEGY):
    merger = get_merger(merge_strategy)
    result = merger.merge(a, b)
    return result
