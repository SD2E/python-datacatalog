import os
import sys
import importlib
import inspect
import itertools
from pprint import pprint
from .. import settings
from ..utils import dynamic_import
from .coll import JSONSchemaCollection

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

STORE_SCHEMAS = ['linkedstores.basestore',
                 'linkedstores.challenge_problem',
                 'linkedstores.experiment_design',
                 'linkedstores.structured_request',
                 'linkedstores.experiment',
                 'linkedstores.sample',
                 'linkedstores.measurement',
                 'linkedstores.file',
                 'linkedstores.fixity',
                 'linkedstores.pipeline',
                 'linkedstores.pipelinejob',
                 'linkedstores.product',
                 'linkedstores.reference',
                 'linkedstores.process',
                 'linkedstores.association',
                 'linkedstores.annotations.tag',
                 'linkedstores.annotations.text']

"""Modules that define object and document schemas for managed document
collections linked by UUID and linkage fields. Classes in these modules inherit
schema and database logic from ``basestore`` classes
"""

COMPOSED_SCHEMAS = ['compositions.sample_set']
"""Modules that represent compositions or translations of existing datacatalog
schemas. These are useful for backwards or sideways compatibility."""

PRIMITIVE_SCHEMAS = ['definitions', 'filetypes', 'identifiers',
                     'tenancy', 'managers.annotations']
"""Modules that define simple patterns, enumerators, or static foreign entities
"""

UNMANAGED_SCHEMAS = ['formats']
"""Modules that define schemas imported from outside the core datacatalog data
model into the shared datacatalog schema namespace"""

SCHEMAS = [STORE_SCHEMAS, COMPOSED_SCHEMAS,
           PRIMITIVE_SCHEMAS, UNMANAGED_SCHEMAS]
"""The union set of all schemas. This list is traversed when building the set
of all project schemas."""


def get_all_schemas(filters=[]):
    """Top-level function to discover and return all known JSON schemas

    Args:
        filters (list, optional): subset list of classes to traverse

    Returns:
        JSONSchemaCollection: Collection of schemas indexed by filename
    """
    schemata = JSONSchemaCollection(dict())
    for pkg in list(itertools.chain.from_iterable(SCHEMAS)):
        if isinstance(filters, list) and filters != []:
            if pkg not in filters:
                continue
        m = dynamic_import('.' + pkg + '.schemas', package='datacatalog')
        package_schemas = m.get_schemas()
        schemata = {**schemata, **package_schemas}
    return schemata
