import re

__all__ = ['IndexRequest', 'IndexingError', 'FilesLister']

# from ...definitions.enumclasses import processing_level

class IndexRequest(object):
    PARAMS = [('processing_level', True, 'processing_level', '1'),
              ('filters', True, 'filters', []),
              ('note', False, 'note', None),
              ('fixity', False, 'fixity', True)]

    def __init__(self, **kwargs):
        for param, mandatory, attr, default in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory else kwargs.get(param, default))
            except KeyError:
                pass
            setattr(self, attr, value)

    def as_dict():
        pass

    def regex(self):
        """Compile the request's filters list into a Python regex
        """
        return re.compile('|'.join(getattr(self, 'filters', [])))

class FilesLister(object):
    def __init__(self, agave_client, index_request):
        pass

class IndexingError(Exception):
    """An error has occurred during setup or execution of an indexing task
    """
    pass
