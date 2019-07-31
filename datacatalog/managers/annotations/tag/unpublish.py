import os
import json
from ..schemabase import EventBaseSchema
from datacatalog.tokens import (
    validate_token, validate_admin_token)
from ..anno import (DeletedRecordCounts, AssociatedAnnotation)

class TagAnnotationUnpublishSchema(EventBaseSchema):
    DEFAULT_DOCUMENT_NAME = 'publish.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'rb'))
        super().__init__(**j)
        self.update_id()

class Schema(TagAnnotationUnpublishSchema):
    pass
def unpublish(self, body, token=None):
    self.logger.debug('event.unpublish')
    raise NotImplementedError()
    validate_admin_token(token, permissive=False)
    return self.unpublish_tag(token=token, **body)
