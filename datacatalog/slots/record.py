from attrdict import AttrDict
from . import dbkey, status


def new_slot(username, value=None):
    rec = {'name': dbkey.new_keyname(username),
           'value': {'body': value,
                     'status': status.CREATED}}
    return AttrDict(rec)
