import inspect
import json
import os
import sys
from pprint import pprint

from ...dicthelpers import data_merge
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, JSONSchemaCollection, linkages
from ..basestore.exceptions import CatalogError

DEFAULT_LINK_FIELDS = [linkages.CHILD_OF]

class SampleUpdateFailure(CatalogUpdateFailure):
    pass

class SampleDocument(HeritableDocumentSchema):
    """Defines one of the samples in an experiment"""

    def __init__(self, inheritance=True, **kwargs):
        super(SampleDocument, self).__init__(inheritance, **kwargs)
        self.update_id()


class SampleStore(LinkedStore):

    LINK_FIELDS = DEFAULT_LINK_FIELDS

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        """Manage storage and retrieval of SampleDocuments"""
        super(SampleStore, self).__init__(mongodb, config, session)
        schema = SampleDocument(**kwargs)
        super(SampleStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))

    # Unset all instances of a list of fields on this samples collection for a given experiment id
    # Experiment id must be namespaced
    # Fields must be declared, optional, not an index or managed by the store
    def clean_fields(self, experiment_id, fields_to_clean):
        self.logger.debug('clean fields() {} {}'.format(experiment_id, fields_to_clean))

        if len(fields_to_clean) == 0:
            raise ValueError("Must specify at least one field to clean")

        if not experiment_id.startswith("experiment"):
            raise ValueError("Experiment id is not namespaced '{}'".format(experiment_id))

        # validate that fields are present and optional per schema
        all_fields = self.get_fields()
        uuid_fields = self.get_uuid_fields()
        required_fields = self.get_required()

        fields_to_clean_obj = {}
        for field_to_clean in fields_to_clean:
            if field_to_clean in uuid_fields:
                raise ValueError("Field to clean is a uuid field '{}'".format(field_to_clean))
            if field_to_clean in self.TOKEN_FIELDS:
                raise ValueError("Field to clean is a token field '{}'".format(field_to_clean))
            if field_to_clean in self.READONLY_FIELDS:
                raise ValueError("Field to clean is a read only field '{}'".format(field_to_clean))
            if field_to_clean not in all_fields:
                raise ValueError("Field to clean is not declared '{}'".format(field_to_clean))
            if field_to_clean in required_fields:
                raise ValueError("Field to clean is required '{}'".format(field_to_clean))

            fields_to_clean_obj[field_to_clean] = ""

        # sample.lab.sample_id.experiment.lab.experiment_id
        # sample.transcriptic.aq1etu3rz6cf3yc.experiment.transcriptic.r1ett8nq3wbmef
        try:
            update_many_result = self.coll.update_many({ "sample_id" : { "$regex" : "^sample.*" + experiment_id + "$" } }, { "$unset" : fields_to_clean_obj })
            return update_many_result
        except Exception as exc:
            raise CatalogError('Failed to clean fields', exc)

class StoreInterface(SampleStore):
    pass
