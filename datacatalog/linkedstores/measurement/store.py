import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, JSONSchemaCollection, linkages
DEFAULT_LINK_FIELDS = [linkages.CHILD_OF]

class MeasurementUpdateFailure(CatalogUpdateFailure):
    pass

class MeasurementDocument(HeritableDocumentSchema):
    """Defines a measurement in a sample"""

    def __init__(self, inheritance=True, **kwargs):
        super(MeasurementDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class MeasurementStore(LinkedStore):
    """Manage storage and retrieval of MeasurementDocuments"""

    LINK_FIELDS = DEFAULT_LINK_FIELDS

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(MeasurementStore, self).__init__(mongodb, config, session)
        schema = MeasurementDocument(**kwargs)
        super(MeasurementStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))

class StoreInterface(MeasurementStore):
    """Generic interface to MeasurementStore"""
    pass
