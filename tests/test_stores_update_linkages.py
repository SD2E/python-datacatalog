import os
import pytest
import sys
import yaml
import json

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
from fixtures.mongodb import mongodb_settings, mongodb_authn
from data import file, updatelinkages

sys.path.insert(0, '/')
import datacatalog


# def test_files_linkages_add(mongodb_settings):
#     base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
#     for key, doc, uuid_val in file.CREATES:
#         resp = base.add_revise_document(doc)
#         assert resp['uuid'] is not None

# def test_files_linkages_update(mongodb_settings):
#     base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
#     for key, doc, uuid_val in file.UPDATES:
#         resp = base.add_revise_document(doc, uuid=uuid_val)
#         assert resp['uuid'] == uuid_val

# def test_files_delete(mongodb_settings):
#     base = datacatalog.linkedstores.file.FileStore(mongodb_settings)
#     for key, doc, uuid_val in file.DELETES:
#         resp = base.delete_document(uuid_val)
#         assert resp.raw_result == {'n': 1, 'ok': 1.0}
