import uuid
from .. import typeduuid

def test_create():
    m = typeduuid.catalog_uuid('abdefgh', 'generic', binary=False)
    assert m.startswith(typeduuid.uuidtypes['generic'].prefix)

def test_classify_text_uuid():
    m = typeduuid.catalog_uuid('abdefgh', 'generic', binary=False)
    t = typeduuid.get_uuidtype(m)
    assert t == 'generic'

def test_classify_object_uuid():
    m = typeduuid.catalog_uuid('abdefgh', 'generic', binary=False)
    n = uuid.UUID(m)
    t = typeduuid.get_uuidtype(n)
    assert t == 'generic'
