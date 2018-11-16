import uuid
from .. import typed_uuid

def test_create():
    m = typed_uuid.catalog_uuid('abdefgh', 'generic', binary=False)
    assert m.startswith(typed_uuid.UUIDType['generic'].prefix)

def test_classify_text_uuid():
    m = typed_uuid.catalog_uuid('abdefgh', 'generic', binary=False)
    t = typed_uuid.get_uuidtype(m)
    assert t == 'generic'

def test_classify_object_uuid():
    m = typed_uuid.catalog_uuid('abdefgh', 'generic', binary=False)
    n = uuid.UUID(m)
    t = typed_uuid.get_uuidtype(n)
    assert t == 'generic'
