import os
import json
from datacatalog.jsonschemas import JSONSchemaBaseObject
from datacatalog.jsonschemas.objects import get_class_object

__all__ = ['EventBaseSchema']

class EventBaseSchema(JSONSchemaBaseObject):
    """Placeholder class for a parent schema for management events"""
    DEFAULT_DOCUMENT_NAME = 'schema.json'

    # def __init__(self, **kwargs):
    #     schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
    #     if os.path.exists(schemafile):
    #         j = json.load(open(schemafile, 'rb'))
    #     else:
    #         j = dict()
    #     super(EventBaseSchema, self).__init__(**j)
    #     self.update_id()

    def to_class(self):
        """Create a Python class from the schema object
        """
        return get_class_object(self.to_dict())
