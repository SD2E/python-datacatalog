import json
import os
import sys
from pprint import pprint

from ..jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from ..utils import dynamic_import

HERE = os.path.abspath(__file__)
PARENT = os.path.dirname(HERE)

class ViewSchema(JSONSchemaBaseObject):
    pass

def get_schemas():
    """Return all definition sub-schema(s)

    Returns:
        JSONSchemaCollection: One or more schemas
    """
    schemas = dict()
    mod = dynamic_import('datacatalog.views')
    for meth in dir(mod):
        if not meth.startswith('_'):
            try:
                pkg = dynamic_import('datacatalog.views.' + meth + '.schemas')
                pkg_schemas = pkg.get_schemas()
                for k, v in pkg_schemas.items():
                    schemas[k] = v
            except ModuleNotFoundError:
                pass
            except NotImplementedError:
                # print('{} is not indexable'.format(meth))
                pass

    return JSONSchemaCollection(schemas)

# def get_aggregations():
#     """Return all definition sub-schema(s)

#     Returns:
#         JSONSchemaCollection: One or more schemas
#     """
#     mod = dynamic_import('datacatalog.views')
#     for meth in dir(mod):
#         if not meth.startswith('_'):
#             try:
#                 pkg = dynamic_import('datacatalog.views.' + meth + '.schemas')
#                 pprint(pkg.get_schemas())
#             except ModuleNotFoundError:
#                 pass
#             except NotImplementedError:
#                 print('{} is not indexable'.format(meth))
