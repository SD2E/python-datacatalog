from datacatalog.extensible import ExtensibleAttrDict

__all__ = ['CHILD_OF', 'GENERATED_BY', 'DERIVED_FROM', 'DERIVED_USING',
           'ACTED_ON', 'ACTED_USING', 'CONNECTED_BY', 'CONNECTED_TO',
           'DEFAULT_LINKS', 'ALL', 'Linkage',
           'LinkageError', 'LinkEdges', 'LinkEdgesDiff']

CHILD_OF = 'child_of'
GENERATED_BY = 'generated_by'
DERIVED_FROM = 'derived_from'
DERIVED_USING = 'derived_using'
ACTED_ON = 'acted_on'
ACTED_USING = 'acted_using'
CONNECTS_FROM = 'connects_from'
CONNECTS_TO = 'connects_to'

DEFAULT_LINKS = (CHILD_OF, DERIVED_FROM, DERIVED_USING, GENERATED_BY)
ALL = (CHILD_OF, DERIVED_FROM, DERIVED_USING, GENERATED_BY,
       ACTED_ON, ACTED_USING, CONNECTS_TO, CONNECTS_FROM)

DEFINITIONS = {CHILD_OF: 'B is immutably connected to A',
               GENERATED_BY: 'B was created by process or behavior of A',
               DERIVED_FROM: 'A was an input in creating B and B materially contains contents of A',
               DERIVED_USING: 'A was needed to create B but B does not contain contents of A',
               ACTED_ON: 'B acted on A',
               ACTED_USING: 'B acted using A',
               CONNECTS_FROM: 'Association C connects A to B',
               CONNECTS_TO: 'Association C connects B to A'}

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
        if link_fields is None or not isinstance(link_fields, (list, tuple)):
            link_fields = DEFAULT_LINKS
        setattr(self, 'LINK_FIELDS', link_fields)
        for lf in link_fields:
            lf_val = Linkage(lf)
            setattr(self, lf_val, doc_dict.get(lf, []))

    def right_merge(self, other, extend_only=True):
        links = MergedLinkages()
        for lfv in self.LINK_FIELDS:
            lf = Linkage(lfv)
            links_set1 = set(getattr(self, lf, list()))
            links_set2 = set(getattr(other, lf, list()))
            # Extend
            union = links_set1.union(links_set2)
            if extend_only is False:
                # Remove any that are only on the left
                left_only_set = links_set1 - links_set2
                union = union - left_only_set
            links['values'][lf] = list(union)
            links['values'][lf].sort()
            if links['values'][lf] != list(links_set1):
                links.mark_updated()
        return links


def merge_linkages(document_a, document_b, link_fields=None):
    le1 = LinkEdges(document_a, link_fields=link_fields)
    le2 = LinkEdges(document_b, link_fields=link_fields)
    return le1.right_merge(le2)
