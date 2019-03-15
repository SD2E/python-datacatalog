__all__ = ['MERGE', 'REPLACE', 'DROP', 'ALL', 'DEFAULT_STRATEGY', 
           'Strategy', 'StrategyError']

MERGE = 'merge'
REPLACE = 'replace'
DROP = 'drop'

DEFINITIONS = {MERGE: 'Right-favoring merge A and B',
               REPLACE: 'Replace A with B',
               DROP: 'Drop A then write B'}

ALL = (MERGE, REPLACE, DROP)
DEFAULT_STRATEGY = MERGE

class StrategyError(ValueError):
    pass

class Strategy(str):
    """A document update strategy"""
    def __new__(cls, value):
        value = str(value).lower()
        setattr(cls, 'description', DEFINITIONS.get(value))
        if value not in list(DEFINITIONS.keys()):
            raise StrategyError('"{}" is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)
 