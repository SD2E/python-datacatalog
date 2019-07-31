import os
import json
from ..schemabase import EventBaseSchema
from ..anno import (DeletedRecordCounts, AssociatedAnnotation)

class TagAnnotationLinkSchema(EventBaseSchema):
    DEFAULT_DOCUMENT_NAME = 'link.json'

    def __init__(self, **kwargs):
        schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
        j = json.load(open(schemafile, 'rb'))
        super().__init__(**j)
        self.update_id()

class Schema(TagAnnotationLinkSchema):
    pass

def action(self, body, token=None):
    self.logger.info('event.link')
    return new_tag_association(self, token=token, **body)

def new_tag_association(self,
                        connects_from=None,
                        connects_to=None,
                        owner=None,
                        token=None,
                        **kwargs):
    """Associates a Tag with one or more Data Catalog records.

    Args:
        connects_from (str): UIUD of the Tag (connects_from)
        connects_to (str/list): UUID (or list) of Records to connect with
        owner (str, optional): TACC.cloud username owning the association

    Returns:
        tuple: The newly created (or updated) Association
    """
    assoc = self._new_annotation_association(
        connects_from, connects_to,
        owner=owner, token=token, **kwargs)
    return assoc
