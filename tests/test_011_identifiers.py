import os
import pytest
from .data import identifiers
from datacatalog import identifiers as identifiers_module
from datacatalog.identifiers import typeduuid

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_v1_v2_uuid_mapping():
    for utype, utext, v1uuid, v2uuid in identifiers.CASES:
        new_v2_uuid = identifiers_module.typeduuid.catalog_uuid_from_v1_uuid(v1uuid, utype)
        assert new_v2_uuid == v2uuid

def test_v1_v2_named_uuid_mapping():
    for utype, utext, v1uuid, v2uuid in identifiers.CASES:
        new_v2_uuid = identifiers_module.typeduuid.catalog_uuid(utext, utype)
        assert new_v2_uuid == v2uuid

@pytest.mark.parametrize("uuid, permissive, result, raises", [
    (None, True, False, False),
    (None, False, False, True),
    ('meep', True, False, False),
    ('meep', False, False, True),
    ([], True, False, False),
    ([], False, False, True),
    ('1027aa77-d524-5359-a802-a8008adaecb5', True, True, False),
    ('1027aa77-d524-5359-a802-a8008adaecb5', False, True, False),
    ('5027aa77-d524-5359-a802-a8008adaecb5', True, True, False),
    ('5027aa77-d524-5359-a802-a8008adaecb5', False, True, False),
    # Technically these are UUID1
    ('4d1f70a0-b924-11e9-ae8d-acbc32822af9', True, True, False),
    ('4d1f70a0-b924-11e9-ae8d-acbc32822af9', False, True, False)
])
def test_validate_uuid5(uuid, permissive, result, raises):
    if raises:
        with pytest.raises(Exception):
            typeduuid.validate_uuid5(uuid, permissive=permissive)
    else:
        assert typeduuid.validate_uuid5(uuid, permissive=permissive) == result


@pytest.mark.parametrize("uuid, result, raises", [
    (None, None, True),
    ('meep', None, True),
    ('1027aa77-d524-5359-a802-a8008adaecb5', 'experiment', False),
    ('5027aa77-d524-5359-a802-a8008adaecb5', None, True),
    ('4d1f70a0-b924-11e9-ae8d-acbc32822af9', None, True),
])
def test_get_uuidtype(uuid, result, raises):
    if raises:
        with pytest.raises(Exception):
            typeduuid.get_uuidtype(uuid)
    else:
        assert typeduuid.get_uuidtype(uuid) == result


@pytest.mark.parametrize("uuid_str, result, raises", [
    (None, [], False),
    ([None], [], False),
    ('1027aa77-d524-5359-a802-a8008adaecb5', ['1027aa77-d524-5359-a802-a8008adaecb5'], False),
    (['1027aa77-d524-5359-a802-a8008adaecb5'], ['1027aa77-d524-5359-a802-a8008adaecb5'], False),
    (['1027aa77-d524-5359-a802-a8008adaecb5', '1166d16b-4c87-5ead-a25a-60ae90b527fb'], ['1027aa77-d524-5359-a802-a8008adaecb5', '1166d16b-4c87-5ead-a25a-60ae90b527fb'], False),
    (['1166d16b-4c87-5ead-a25a-60ae90b527fb', '1027aa77-d524-5359-a802-a8008adaecb5'], ['1027aa77-d524-5359-a802-a8008adaecb5', '1166d16b-4c87-5ead-a25a-60ae90b527fb'], False),
    (['1027aa77-d524-5359-a802-a8008adaecb5', '5027aa77-d524-5359-a802-a8008adaecb5'], ['1027aa77-d524-5359-a802-a8008adaecb5'], False)
])
def test_listify_uuid(uuid_str, result, raises):
    if raises:
        with pytest.raises(Exception):
            typeduuid.listify_uuid(uuid_str)
    else:
        lst = typeduuid.listify_uuid(uuid_str)
        assert lst == result

