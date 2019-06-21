"""Exposes Tag-related AnnotationManager functions via a messaging interface
"""
from datacatalog.slots import Slot, SlotNotReady
from .anno import AnnotationManager
from datacatalog.linkedstores.basestore import (
    validate_token, validate_admin_token)

EVENT_NAMES = ('create', 'delete', 'link', 'unlink', 'publish', 'unpublish')

class TagAnnotationManager(AnnotationManager):

    def handle(self, msg, slot=None, token=None, **kwargs):

        # Body must exist and be a dict
        if 'body' not in msg:
            raise KeyError('Message requires a "body" field')
        if not isinstance(msg.get('body', None), dict):
            raise ValueError('Message "body" must be a dictionary object')
        body = msg.get('body')

        # Sanity check action field
        try:
            event_name = msg.get('action')
            if event_name not in EVENT_NAMES:
                raise ValueError(
                    '"{}" is an invalid value for "action"'.format(event_name))
            event_name = event_name.lower()
        except KeyError:
            raise KeyError('Message must have an "action" field')

        # Get authz token
        token = msg.get('token', token)

        # Get persistence slot (or gracefully ignore None). The slot must have
        # been created before it is written to
        slot_client = None
        slot_name = msg.get('slot', slot)
        if slot_name is not None:
            slot_client = Slot(self.client, name=slot_name)

        self.logger.info('Handling event "{}"'.format(event_name))
        func = getattr(self, event_name)
        resp = func(body, token=token, **kwargs)

        if slot_client is not None:
            self.logger.info('Writing response to slot: {}'.format(resp))
            try:
                slot_client.write(resp, slot_name)
            except Exception as exc:
                self.logger.error(
                    'Failed writing slot {}: {}'.format(slot_name, exc))

        return resp

    def create(self, body, token=None):
        # TODO - Allow create-and-link by passing 1+ record UUID?
        self.logger.debug('event.create: {}'.format(body))
        return self.new_tag(token=token, **body)

    def delete(self, body, token=None):
        self.logger.debug('event.delete')
        validate_admin_token(token, permissive=False)
        return self.delete_tag(token=token, **body)

    def link(self, body, token=None):
        self.logger.debug('event.link')
        return self.new_tag_association(token=token, **body)

    def unlink(self, body, token=None):
        self.logger.debug('event.unlink')
        raise NotImplementedError()

    def publish(self, body, token=None):
        self.logger.debug('event.publish')
        validate_admin_token(token, permissive=False)
        return self.publish_tag(token=token, **body)

    def unpublish(self, body, token=None):
        self.logger.debug('event.unpublish')
        validate_admin_token(token, permissive=False)
        return self.unpublish_tag(token=token, **body)
