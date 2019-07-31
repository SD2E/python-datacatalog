import json
from agavepy.agave import Agave, AgaveError
from . import logger, record, status


class SlotNotReady(ValueError):
    pass


class Slot(object):
    def __init__(self, agave, name=None):
        self.logger = logger.get_logger()
        self.client = agave
        self.name = name
        self.uuid = None

    def _get_username(self):
        # TODO - Make this more robust
        return self.client.token.username

    def _filter_record(self, meta_dict, uuid=True, raw=False):

        if raw is False:
            for k in ['_links', 'owner',
                      'schemaId',
                      'internalUsername',
                      'associationIds',
                      'lastUpdated',
                      'created']:
                if k in meta_dict:
                    del meta_dict[k]

        if uuid is False:
            try:
                del meta_dict['uuid']
            except KeyError:
                pass

        return meta_dict

    def create(self):
        self.logger.debug('Top of create(): {}')
        username = self._get_username()
        self.logger.debug('Username: {}'.format(username))
        rec = record.new_slot(username)
        meta = json.dumps(rec)
        self.logger.debug('Record: {}'.format(meta))
        try:
            resp = self.client.meta.addMetadata(body=meta)
            setattr(self, 'name', rec.name)
            self.logger.info('Name: {}'.format(self.name))
            setattr(self, 'uuid', resp['uuid'])
            self.logger.debug('Uuid: {}'.format(self.uuid))
        except Exception as e:
            self.logger.warning(e)
            raise
        return self

    def read(self, key_name=None, raw=False, delete=False):
        """Returns the contents of a slot

        Arguments:
            key_name (str, optional): Slot name. Defaults to current slot if not defined.
            raw (bool, optional): Whether to return value or entire slot body
            delete (bool, optional): Delete the slot after reading it
        """
        if key_name is None:
            if getattr(self, 'name', None) is None:
                raise SlotNotReady(
                    'Cannot read from self before calling init()')
            else:
                key_name = getattr(self, 'name')
        self.logger.info('Read: {}'.format(key_name))

        resp = None
        query = json.dumps({'name': key_name})
        self.logger.debug('Query: {}'.format(query))

        objs = self.client.meta.listMetadata(q=query)
        self.logger.debug('Response: {}'.format(objs))

        return_val = None
        if isinstance(objs, list) and len(objs) > 0:
            resp = objs[0]
        else:
            raise ValueError('Slot "{}" was not found'.format(key_name))
        if raw is False:
            return_val = resp.get('value', {}).get('body')
        else:
            return_val = resp

        if delete:
            try:
                del_uuid = resp.get('uuid')
                self.client.meta.deleteMetadata(uuid=del_uuid)
                if self.uuid == del_uuid:
                    setattr(self, 'client', None)
                    setattr(self, 'uuid', None)
                    setattr(self, 'name', None)
            except Exception as err:
                self.logger.exception(str(err))

        return return_val

    def status(self, key_name=None):
        if key_name is None:
            if getattr(self, 'name', None) is None:
                raise SlotNotReady(
                    'Cannot inspect status for self before calling init()')
            else:
                key_name = getattr(self, 'name')
        obj = self.read(key_name, raw=True)
        return obj.get('value', {}).get('status')

    def ready(self, key_name=None):
        stat = self.status(key_name)
        if stat == status.READY:
            return True
        else:
            return False

    @property
    def value(self):
        return self.read(raw=False)

    def write(self, value, key_name=None, raw=False):
        if key_name is None:
            if getattr(self, 'name', None) is None:
                raise SlotNotReady(
                    'Cannot write value to self before calling init()')
            else:
                key_name = getattr(self, 'name')
        self.logger.info('Write: {}'.format(key_name))

        obj = self.read(key_name, raw=True)
        obj_uuid = obj.pop('uuid')

        obj_status = obj.get('value', {}).get('status', None)
        if obj_status != status.CREATED:
            raise ValueError('Record has already been written')

        obj['value'] = {'body': value, 'status': status.READY}
        meta = json.dumps(obj)
        resp = self.client.meta.updateMetadata(uuid=obj_uuid, body=meta)
        if 'uuid' not in resp:
            raise AgaveError('Failure writing to Tapis metadata store')
        return self

    def __repr__(self):
        if getattr(self, 'name', None) is not None:
            return self.name
        else:
            return '<' + self.__class__.__name__ + '>'
