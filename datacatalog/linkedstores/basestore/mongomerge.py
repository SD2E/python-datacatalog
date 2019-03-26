from datacatalog import linkages
from datacatalog.mongo import ReturnDocument
from .merge import DEFAULT_JSONMERGE_STRATEGY
from . import managedfields

FILTER_FIELDS = tuple(set(managedfields.PRIVATE + linkages.ALL))

def pre_merge_filter(document):
    """Private: Strip managed & linkage fields before merging
    """
    filter_contents = dict()
    for field in FILTER_FIELDS:
        if field in document:
            filter_contents[field] = document.pop(field)
    return document, filter_contents
