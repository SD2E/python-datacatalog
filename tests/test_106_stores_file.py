import pytest
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

from datacatalog.linkedstores.file import FileStore, FileRecord
from datacatalog.jsonschemas import ValidationError
from datacatalog.utils import safen_path
from .data import file

def test_files_db_init(mongodb_settings):
    base = FileStore(mongodb_settings)
    assert base is not None

def test_file_db_heritable_schema(mongodb_settings):
    base = FileStore(mongodb_settings)
    assert 'name' in base.get_indexes()
    assert 'title' not in base.get_indexes()

def test_files_schema(mongodb_settings):
    base = FileStore(mongodb_settings)
    assert isinstance(base.schema, dict)

def test_files_name(mongodb_settings):
    base = FileStore(mongodb_settings)
    assert base.name == 'files'

def test_files_uuid_tytpe(mongodb_settings):
    base = FileStore(mongodb_settings)
    assert base.get_uuid_type() == 'file'

def test_files_issue_uuid_string(mongodb_settings):
    base = FileStore(mongodb_settings)
    filename = 'science-results.xlsx'
    identifier_string_uuid = base.get_typeduuid(filename, binary=False)
    assert identifier_string_uuid == '1059e14b-a341-5804-ac69-5c731f6ecf80'

def test_files_issue_uuid_dict(mongodb_settings):
    base = FileStore(mongodb_settings)
    filename = 'science-results.xlsx'
    filedict = {'name': filename,
                'file_id': 'file.tacc.wierdscience1985',
                'not_in_schema': 123}
    identifier_string_uuid = base.get_typeduuid(filedict, binary=False)
    assert identifier_string_uuid == '1059e14b-a341-5804-ac69-5c731f6ecf80'

def test_files_addfails_invalid_uuid(mongodb_settings):
    base = FileStore(mongodb_settings)
    uuid_val = '9999e14b-a341-5804-ac69-5c731f6ecf80'
    filename = 'science-results.xlsx'
    filedict = {'name': filename,
                'file_id': 'file.tacc.wierdscience1985'}
    with pytest.raises(ValueError):
        base.add_update_document(filedict, uuid=uuid_val)

def test_files_addfails_schema_validation_fails(mongodb_settings):
    base = FileStore(mongodb_settings)
    uuid_val = '9999e14b-a341-5804-ac69-5c731f6ecf80'
    filename = 'science-results.xlsx'
    filedict = {'name': filename,
                'file_id': 'tacc.file.wierdscience1985'}
    with pytest.raises(ValueError):
        base.add_update_document(filedict, uuid=uuid_val)

def test_files_addfails_passed_uuid_mismatch_computed(mongodb_settings):
    base = FileStore(mongodb_settings)
    uuid_val = '1059e14b-a341-5804-ac69-5c731f6ecf90'
    filename = 'science-results.xlsx'
    filedict = {'name': filename,
                'file_id': 'file.tacc.wierdscience1985'}
    with pytest.raises(ValueError):
        base.add_update_document(filedict, uuid=uuid_val)

def test_files_addfails_uuids_mismatch(mongodb_settings):
    base = FileStore(mongodb_settings)
    uuid_val = '1059e14b-a341-5804-ac69-5c731f6ecf81'
    filename = 'science-results.xlsx'
    filedict = {'name': filename,
                'file_id': 'file.tacc.wierdscience1985',
                'uuid': '1059e14b-a341-5804-ac69-5c731f6ecf80'}
    with pytest.raises(ValueError):
        base.add_update_document(filedict, uuid=uuid_val)

def test_files_au_add(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.CREATES:
        resp = base.add_update_document(doc)
        assert resp['uuid'] is not None
        assert '_update_token' in resp

def test_files_au_replace(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val, strategy='replace')
        assert resp['uuid'] == uuid_val
        assert '_update_token' in resp

def test_files_au_update(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_update_document(doc, uuid=uuid_val, strategy='merge')
        assert resp['uuid'] == uuid_val
        assert '_update_token' in resp

def test_files_links_get_links(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        links = base.get_links(uuid_val, 'child_of')
        assert isinstance(links, list)

def test_files_links_add_link(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_link(uuid_val, '1040f664-a654-0b71-4189-2ac6f77a05a7', 'child_of')
        assert resp is True
        links = base.get_links(uuid_val, 'child_of')
        assert '1040f664-a654-0b71-4189-2ac6f77a05a7' in links

def test_files_links_add_link(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_link(uuid_val, ['1040f664-a654-0b71-4189-2ac6f77a05a7', '104dae4d-a677-5991-ae1c-696d2ee9884e',
        '10483e8d-6602-532a-8941-176ce20dd05a'], 'child_of')
        assert resp is True
        links = base.get_links(uuid_val, 'child_of')
        assert '1040f664-a654-0b71-4189-2ac6f77a05a7' in links

def test_files_links_remove_link(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.remove_link(uuid_val, '104dae4d-a677-5991-ae1c-696d2ee9884e')
        assert resp is True
        links = base.get_links(uuid_val, 'child_of')
        assert '104dae4d-a677-5991-ae1c-696d2ee9884e' not in links

def test_files_links_add_invalid_linkage(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.UPDATES:
        resp = base.add_link(uuid_val, '1040f664-a654-0b71-4189-2ac6f77a05a7', 'acted_on')
        assert resp is False

@pytest.mark.parametrize("filename,fuuid", [
    ('/uploads/science-results.xlsx', '1056d16b-4c87-5ead-a25a-60ae90b527fb'),
    ('/uploads//science-results.xlsx', '1056d16b-4c87-5ead-a25a-60ae90b527fb')])
def test_files_normpath(mongodb_settings, filename, fuuid):
    base = FileStore(mongodb_settings)
    identifier_string_uuid = base.get_typeduuid(filename, binary=False)
    assert identifier_string_uuid == fuuid

@pytest.mark.delete
def test_files_delete(mongodb_settings):
    base = FileStore(mongodb_settings)
    for key, doc, uuid_val in file.DELETES:
        resp = base.delete_document(uuid_val)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}

def test_files_disk_load(mongodb_settings):
    base = FileStore(mongodb_settings)
    for filename, file_uuid in file.LOADS:
        doc = json.load(open(os.path.join(file.DATADIR, filename), 'r'))
        resp = base.add_update_document(doc, strategy='replace')
        assert resp['uuid'] == file_uuid

@pytest.mark.delete
def test_files_disk_delete(mongodb_settings):
    base = FileStore(mongodb_settings)
    for filename, file_uuid in file.LOADS:
        resp = base.delete_document(file_uuid)
        assert resp.raw_result == {'n': 1, 'ok': 1.0}

@pytest.mark.parametrize("filename,fuuid", [
    ('/uploads/science results.xlsx', '1056d16b-4c87-5ead-a25a-60ae90b527fb'),
    ('/uploads/science-results.xlsx', '1056d16b-4c87-5ead-a25a-60ae90b527fb')])
def test_files_safen_path(mongodb_settings, filename, fuuid):
    """Verify that regular and url-encoded paths are equivalent
    """
    base = FileStore(mongodb_settings)
    doc = FileRecord({'name': filename})
    resp = base.add_update_document(doc)
    assert resp['uuid'] == fuuid

def test_safen_path():
    """A safen path special case with equals
    """
    unsafe = "variants-forA=B-samp=ling"
    still_unsafe = safen_path(unsafe, no_unicode=True, no_spaces=True)
    assert still_unsafe == "variants-forA=B-samp=ling"

    now_safe = safen_path(unsafe, no_unicode=True, no_spaces=True, no_equals=True)
    assert now_safe == "variants-forA-B-samp-ling"

@pytest.mark.parametrize("filename,storage_system,resolved_storage_system", [
    ('/uploads/science results1.xlsx', 'data-sd2e-community', 'data-sd2e-community'),
    ('/uploads/science results2.xlsx', None, 'data-sd2e-community'),
    ('/sd2eadm/config.yml', 'data-sd2e-projects-users', 'data-sd2e-projects-users')])
def test_uses_storage_system(mongodb_settings, filename, storage_system, resolved_storage_system):
    base = FileStore(mongodb_settings)
    doc = FileRecord({'name': filename, 'storage_system': storage_system})
    resp = base.add_update_document(doc)
    assert resp['storage_system'] == resolved_storage_system

@pytest.mark.parametrize("filename,sys_id_1,sys_id_2,diff", [('/uploads/science-results.xlsx', 'data-sd2e-community', 'data-tacc-work-sd2eadm', True)])
def test_file_id_incorps_system_id(filename, sys_id_1, sys_id_2, diff):
    doc1 = FileRecord({'name': filename, 'storage_system': sys_id_1})
    doc2 = FileRecord({'name': filename, 'storage_system': sys_id_2})

    fid1_v20 = FileStore.generate_string_id_v2_0(doc1)
    fid2_v20 = FileStore.generate_string_id_v2_0(doc2)
    assert fid1_v20 == fid2_v20

    fid1_v21 = FileStore.generate_string_id(doc1)
    fid2_v21 = FileStore.generate_string_id(doc2)

    if diff:
        assert fid1_v21 != fid2_v21
    else:
        assert fid1_v21 == fid2_v21
