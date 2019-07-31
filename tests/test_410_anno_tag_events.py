import os
import pytest
import sys
import yaml
import json
import warnings
from . import longrun, delete
from . import data
from .fixtures.mongodb import mongodb_settings
from .fixtures.agave import agave, credentials

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog import slots, tokens, utils
from datacatalog.managers import annotations

@pytest.fixture(scope='session')
def admin_key():
    return tokens.admin.get_admin_key()

@pytest.fixture(scope='session')
def admin_token(admin_key):
    return tokens.admin.get_admin_token(admin_key)

# create
@pytest.mark.parametrize('tag_name,tag_desc,tag_owner,test_pass', [
    ('tests.pepperoni', 'The best pizza ingredient', 'public', True)
])
def test_tag_anno_event_create(mongodb_settings, agave, admin_token,
                               tag_name, tag_desc, tag_owner, test_pass):

    # TODO - we are hand-building this event which is annoying as we have a schema
    opts = dict()
    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if tag_owner is not None:
        opts['owner'] = tag_owner

    message = {'action': 'create',
               'token': admin_token,
               'body': opts
              }

    manager = annotations.TagAnnotationManager(mongodb_settings, agave=agave)
    resp = manager.handle(message, token=admin_token)
    assert opts['name'] == resp.get('name', None)
    uuid = resp.get('uuid', None)
    admin_mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    if uuid is not None:
        annotations.tag.delete.delete_tag(admin_mgr, uuid, token=admin_token, force=True)
        # admin_mgr.delete_tag(uuid, token=admin_token, force=True)

@pytest.mark.parametrize('tag_name,tag_desc,tag_owner, connects_to, test_pass', [
    ('tests.anchovies', 'Bleh!', 'public',
     '1012da8b-663a-591f-a13d-cdf5277656a0', True),
     ('tests.onions', 'Yum...', 'public',
      ['102e95e6-67a8-5a06-9484-3131c6907890'], True),
     ('tests.peppers', 'Yummier...', 'public',
      ['103246e1-bcdf-5b6e-a8dc-4c7e81b91141',
       '1034c4b8-7c5f-5bd2-b7c1-01cab6022770'], True)])
def test_tag_anno_event_link(mongodb_settings, agave, admin_token,
                                    tag_name, tag_desc, tag_owner,
                                    connects_to, test_pass):

    # TODO - we are hand-building this event which is annoying as we have a schema
    opts = dict()
    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if tag_owner is not None:
        opts['owner'] = tag_owner

    create_msg = {'action': 'create',
                  'token': admin_token,
                  'body': opts
                  }

    # Create the tag
    manager = annotations.TagAnnotationManager(mongodb_settings, agave=agave)
    tag_resp = manager.handle(create_msg, token=admin_token)
    assert opts['name'] == tag_resp.get('name', None)
    tag_uuid = tag_resp.get('uuid', None)

    link_opts = {'connects_from': manager.listify_uuid(tag_uuid),
                 'connects_to': manager.listify_uuid(connects_to),
                 'owner': tag_owner}

    link_msg = {'action': 'link',
                'token': admin_token,
                'body': link_opts
                }

    tag_resp = manager.handle(link_msg, token=admin_token)

    # Listify connects_to and test against array returned from `link`
    connects_to_test = manager.listify_uuid(connects_to)
    assert len(tag_resp) == len(connects_to_test)

@pytest.mark.skip(reason="Update test to unlink rather than delete assoc by UUID.")
@pytest.mark.parametrize('tag_name,tag_desc,tag_owner, connects_to, test_pass', [
    ('tests.pineapple', ':heavenly_light:', 'public',
     '1012da8b-663a-591f-a13d-cdf5277656a0', True),
     ('tests.bacon', 'Woot!', 'sd2eadm',
      ['102e95e6-67a8-5a06-9484-3131c6907890'], True),
     ('tests.chocolate-chips', 'You are a sad, strange little person.', 'public',
      ['103246e1-bcdf-5b6e-a8dc-4c7e81b91141',
       '1034c4b8-7c5f-5bd2-b7c1-01cab6022770'], True)])
def test_tag_anno_event_unlink(mongodb_settings, agave,
                               admin_token, tag_name, tag_desc,
                               tag_owner, connects_to, test_pass):

    # TODO - we are hand-building this event which is annoying as we have a schema
    opts = dict()
    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if tag_owner is not None:
        opts['owner'] = tag_owner

    create_msg = {'action': 'create',
                  'token': admin_token,
                  'body': opts
                  }

    # Create the tag
    manager = annotations.TagAnnotationManager(mongodb_settings, agave=agave)
    tag_resp = manager.handle(create_msg, token=admin_token)
    assert opts['name'] == tag_resp.get('name', None)
    tag_uuid = tag_resp.get('uuid', None)

    link_opts = {'connects_from': manager.listify_uuid(tag_uuid),
                 'connects_to': manager.listify_uuid(connects_to),
                 'owner': tag_owner}

    link_msg = {'action': 'link',
                'token': admin_token,
                'body': link_opts
                }

    link_resp = manager.handle(link_msg, token=admin_token)

    # Array of associations
    for a in link_resp:
        # raise Warning(a)
        unlink_opts = {'uuid': a.get('uuid', None),
                       'owner': tag_owner}

        unlink_msg = {'action': 'unlink',
                      'token': admin_token,
                      'body': unlink_opts}
        unlink_resp = manager.handle(unlink_msg, token=admin_token)
        # assert unlink_resp is None

@pytest.mark.parametrize('tag_name,tag_desc,tag_owner,test_pass', [
    ('tests.jello', 'Very worthy of deletion', 'sd2etest', True)
])
def test_tag_anno_event_delete(mongodb_settings, agave, admin_token,
                               tag_name, tag_desc, tag_owner, test_pass):

    # TODO - we are hand-building this event which is annoying as we have a schema
    opts = dict()
    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if tag_owner is not None:
        opts['owner'] = tag_owner

    message = {'action': 'create',
               'token': admin_token,
               'body': opts
              }

    manager = annotations.TagAnnotationManager(mongodb_settings, agave=agave)
    resp = manager.handle(message, token=admin_token)
    uuid = resp.get('uuid', None)
    admin_mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    if uuid is not None:
        annotations.tag.delete.delete_tag(admin_mgr, uuid,
                                          token=admin_token, force=True)
        # admin_mgr.delete_tag(uuid, token=admin_token, force=True)

    opts = {'uuid': uuid, 'keep_associations': False}
    dmessage = {'action': 'delete',
                'token': admin_token,
                'body': opts
              }
    dresp = manager.handle(dmessage, token=admin_token)
    assert dresp.annotations >= 0
    assert dresp.associations >= 0

# create_slot
@pytest.mark.parametrize('tag_name,tag_desc,tag_owner,test_pass', [
    ('tests.gummibear', 'By Haribo', 'public', True)
])
def test_tag_anno_event_create_slot(mongodb_settings, agave, admin_token,
                                    tag_name, tag_desc, tag_owner, test_pass):

    my_slot = slots.Slot(agave=agave).create()
    opts = dict()
    if tag_name is not None:
        opts['name'] = tag_name
    if tag_desc is not None:
        opts['description'] = tag_desc
    if tag_owner is not None:
        opts['owner'] = tag_owner

    message = {'action': 'create',
               'token': admin_token,
               'slot': my_slot.name,
               'body': opts
              }

    manager = annotations.TagAnnotationManager(mongodb_settings, agave=agave)
    resp = manager.handle(message, token=admin_token)
    uuid = resp.get('uuid', None)
    assert my_slot.ready() is True, 'Slot was not ready'
    persisted_resp = my_slot.read(delete=True)
    assert persisted_resp.get('uuid') == uuid, \
        'Slot uuid did not match function return uuid'

    admin_mgr = annotations.AnnotationManager(mongodb_settings, agave=agave)
    if uuid is not None:
        annotations.tag.delete.delete_tag(admin_mgr, uuid,
                                          token=admin_token, force=True)

# publish
# unpublish
# delete
