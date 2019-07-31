"""Exposes Text-related AnnotationManager functions via a messaging interface
"""
import os
import json
from datacatalog.jsonschemas import JSONSchemaBaseObject
from datacatalog.slots import Slot, SlotNotReady
from .anno import AnnotationManager
from datacatalog.linkedstores.basestore import (
    validate_token, validate_admin_token)

EVENT_NAMES = ('create', 'delete', 'reply')

class TextAnnotationManagerSchema(JSONSchemaBaseObject):
    """Defines Text Annotation Manager events"""
    DEFAULT_DOCUMENT_NAME = 'text.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'rb'))
        super(TextAnnotationManagerSchema, self).__init__(**j)
        self.update_id()

class Schema(TextAnnotationManagerSchema):
    pass
