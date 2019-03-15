from datacatalog.extensible import ExtensibleAttrDict

__all__ = ['CHILD_OF', 'GENERATED_BY', 'DERIVED_FROM', 'DERIVED_USING', 
           'ACTED_ON', 'ACTED_USING', 'DEFAULT_LINKS', 'ALL', 'Linkage',
           'LinkageError', 'LinkEdges', 'LinkEdgesDiff']

CHILD_OF = 'child_of'
GENERATED_BY = 'generated_by'
DERIVED_FROM = 'derived_from'
DERIVED_USING = 'derived_using'
ACTED_ON = 'acted_on'
ACTED_USING = 'acted_on'

DEFAULT_LINKS = (CHILD_OF, DERIVED_FROM, DERIVED_USING, GENERATED_BY)
ALL = (CHILD_OF, DERIVED_FROM, DERIVED_USING, GENERATED_BY, ACTED_ON, ACTED_USING)

DEFINITIONS = {CHILD_OF: 'B is immutably connected to A',
               GENERATED_BY: 'B was created by process or behavior of A',
               DERIVED_FROM: 'A was an input in creating B and B materially contains contents of A',
               DERIVED_USING: 'A was needed to create B but B does not contain contents of A',
               ACTED_ON: 'B acted on A',
               ACTED_USING: 'B acted using A'}

class LinkageError(ValueError):
    pass

class Linkage(str):
    """A linkage type"""
    def __new__(cls, value):
        value = str(value).lower()
        setattr(cls, 'description', DEFINITIONS.get(value))
        if value not in list(DEFINITIONS.keys()):
            raise LinkageError('"{}" is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)

class LinkEdgesDiff(ExtensibleAttrDict):
    left_only = list()
    right_only = list()

class MergedLinkages(ExtensibleAttrDict):
    def __init__(self, links={}):
        self._updated = False
        self.values = links

    @property
    def updated(self):
        return self._updated

    def mark_updated(self):
        setattr(self, '_updated', True)

class LinkEdges(ExtensibleAttrDict):

    def __init__(self, doc_dict, link_fields=None):
        self._updated = False
        if link_fields is None:
            link_fields = DEFAULT_LINKS
        setattr(self, 'LINK_FIELDS', link_fields)
        for lf in link_fields:
            lf_val = Linkage(lf)
            setattr(self, lf_val, doc_dict.get(lf, []))

    # def diff(self, other):
    #     linked_edges = dict()
    #     for lf in self.LINK_FIELDS:
    #         ledff = LinkEdgesDiff()
    #         links1 = getattr(self, lf, list())
    #         links2 = getattr(other, lf, list())
    #         ledff.left_only = list(set(links1) - set(links2))
    #         ledff.right_only = list(set(links2) - set(links1))
    #         linked_edges[lf] = ledff
    #     return linked_edges

    def right_merge(self, other):
        links = MergedLinkages()
        for lf in self.LINK_FIELDS:
            links_set1 = set(getattr(self, lf, list()))
            links_set2 = set(getattr(other, lf, list()))
            # Extend
            union = links_set1.union(links_set2)
            # Remove any that are only on the left
            left_only_set = links_set1 - links_set2
            union = union - left_only_set
            links['values'][lf] = list(union)
            links['values'][lf].sort()
            if links['values'][lf] != list(links_set1):
                links.mark_updated()
        return links


def merge_linkages(document_a, document_b):
    le1 = LinkEdges(document_a)
    le2 = LinkEdges(document_b)
    return le1.right_merge(le2)
