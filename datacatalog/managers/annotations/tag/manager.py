from ..anno import AnnotationManager
from datacatalog.linkedstores.basestore import (
    validate_token, validate_admin_token)
from datacatalog.slots import Slot, SlotNotReady
from datacatalog.utils import dynamic_import
from . import EVENT_NAMES

class TagAnnotationManager(AnnotationManager):

    def handle(self, msg, slot=None, token=None, **kwargs):
        self.logger.debug('Top of TagAnnotationManager#handle')

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
        mod = dynamic_import('.' + event_name, package='datacatalog.managers.annotations.tag')
        # From the schema, materialize a Python class using 'body'
        # This will fail if the message does not validate!
        try:
            self.logger.debug('Validating...')
            mod.Schema().to_class()(**msg)
        except Exception:
            # TODO - Improve error handling and reporting
            raise
        # Each event handler is implemented in <event>.py as #action
        # which in turn calls a named function (i.e. delete_tag)
        # implemented in the same module.
        self.logger.debug('Taking action...')
        func = getattr(mod, 'action')
        resp = func(self, body, token=token, **kwargs)
        # func = getattr(self, event_name)
        # resp = func(body, token=token, **kwargs)

        if slot_client is not None:
            self.logger.info('Writing response to slot: {}'.format(resp))
            try:
                slot_client.write(resp, slot_name)
            except Exception as exc:
                self.logger.error(
                    'Failed writing slot {}: {}'.format(slot_name, exc))

        return resp

