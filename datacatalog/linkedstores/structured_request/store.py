from datacatalog.linkedstores.basestore import (LinkedStore, SoftDelete, JSONSchemaCollection)
from .document import StructuredRequestSchema, StructuredRequestDocument

class StructuredRequestStore(SoftDelete, LinkedStore):
    """Manage storage and retrieval of StructuredRequest documents"""

    def __init__(self, mongodb, config={}, session=None, agave=None, **kwargs):
        super(StructuredRequestStore, self).__init__(mongodb, config, session)
        schema = StructuredRequestSchema(**kwargs)
        super(StructuredRequestStore, self).update_attrs(schema)
        self._enforce_auth = True
        self.setup(update_indexes=kwargs.get('update_indexes', False))

    def new_request(self, name, description=None, owner=None, token=None, **kwargs):
        """Create a new Structured Request

        Args:
            name (str): The structured request's name
            description (str, optional): Optional text description of the structured request

        Returns:
            dict: Representation of the newly-created structured request
        """
        doc = StructuredRequestDocument(name=name,
                                        description=description,
                                        **kwargs)
        return self.add_update_document(doc, token=token)

class StoreInterface(StructuredRequestStore):
    pass