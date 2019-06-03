import collections
from ..common import Manager

Annotation = collections.namedtuple(
    'Annotation', 'record_uuid annotation_uuid association_uuid')

class AnnotationManager(Manager):
    def __init__(self, mongodb, agave=None, *args, **kwargs):
        Manager.__init__(self, mongodb, agave=agave, *args, **kwargs)

    def new_text_anno(self, record_uuid, body=None, owner=None,
                      subject=None, token=None, **kwargs):
        self.validate_tapis_username(owner)
        assoc_uuid = None
        anno = self.stores['text_annotation'].new_text(
            body=body, subject=subject, owner=owner, token=token)
        anno_uuid = anno.get('uuid', None)
        if anno_uuid is not None:
            assoc = self.stores['association'].associate(
                anno_uuid, record_uuid, owner=owner)
            assoc_uuid = assoc.get('uuid', None)
        else:
            raise Exception('Failed to associate record and annotation')

        a = Annotation(annotation_uuid=anno_uuid,
                       association_uuid=assoc_uuid,
                       record_uuid=record_uuid)
        return a

    def reply_text_anno(self, text_anno_uuid, subject, body,
                        owner, token=None, **kwargs):
        self.validate_tapis_username(owner)
        # assoc_uuid = None
        anno = self.stores['text_annotation'].new_reply(
            text_anno_uuid, subject=subject, body=body,
            owner=owner, token=token)
        anno_uuid = anno.get('uuid', None)
        # If we ever decide to create an association even for threaded
        # text annotation docs, we would do it here
        a = Annotation(annotation_uuid=anno_uuid,
                       association_uuid=None,
                       record_uuid=text_anno_uuid)
        return a

    def delete_text_anno(self, text_anno_uuid, token=None, **kwargs):
        # Need to think about how to handle this since it may involve recursion
        pass

    def prune_text_annos(self, record_uuid, token=None, **kwargs):
        # Need to think about how to handle this since it may involve recursion
        pass

    def new_tag_anno(self, record_uuid, name, owner,
                     description='',
                     tag_owner=None,
                     token=None, **kwargs):

        self.validate_tapis_username(owner)
        if tag_owner is not None:
            self.validate_tapis_username(tag_owner)
        else:
            tag_owner = owner

        assoc_uuid = None
        anno = self.stores['tag_annotation'].new_tag(name=name,
                                                     description=description,
                                                     owner=tag_owner,
                                                     token=token, **kwargs)
        anno_uuid = anno.get('uuid', None)
        if anno_uuid is not None:
            assoc = self.stores['association'].associate(
                anno_uuid, record_uuid, owner=owner)
            assoc_uuid = assoc.get('uuid', None)

        a = Annotation(annotation_uuid=anno_uuid,
                       association_uuid=assoc_uuid,
                       record_uuid=record_uuid)
        return a

    def prune_tag_annos(self, record_uuid, token=None, **kwargs):
        pass

    def prune_orphan_annos(self, record_uuid, token=None, **kwargs):
        self.prune_text_annos(record_uuid, token=token, **kwargs)
        self.prune_tag_annos(record_uuid, token=token, **kwargs)
        return True

# Create a Text Anno AND bind to record in one shot
# Create a Text Anno AND bind as child of another in one shot
# Validate usernames via Agave call
# Create and retire Tag and Text associations
# Batch purge by target, source, username
