import json
from pprint import pprint
from ..utils import dynamic_import

class AggregationsCollection(dict):
    """Collection of MongoDB aggregations indexed by view name"""
    def __new__(cls, value):
        return dict.__new__(cls, value)

def get_aggregations():
    """Return all view aggregation definitions

    Returns:
        AggregationsCollection: One or more MongoDB aggregations
    """
    aggs = dict()
    mod = dynamic_import('datacatalog.views')
    for meth in dir(mod):
        if not meth.startswith('_'):
            try:
                pkg = dynamic_import('datacatalog.views.' + meth + '.schemas')
                pkg_aggs = pkg.get_aggregation()
                view_name = pkg.mongodb_view_name
                aggs[view_name] = pkg_aggs
            except ModuleNotFoundError:
                pass
            except NotImplementedError:
                # print('{} is not indexable'.format(meth))
                pass

    return AggregationsCollection(aggs)
