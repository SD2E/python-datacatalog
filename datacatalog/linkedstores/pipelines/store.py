from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import inspect
import json
import os
import sys

from dicthelpers import data_merge
from pathmappings import normalize, abspath
from pprint import pprint

from ..basestore import BaseStore, CatalogUpdateFailure, DocumentSchema, HeritableDocumentSchema, time_stamp, msec_precision
from .schema import PipelineDocument
from .exceptions import PipelineUpdateFailure, DuplicatePipelineError, PipelineUpdateFailure

class PipelineStore(object):
    pass

# class PipelineStore(BaseStore):
#     """Create and manage pipeline records"""
#     def __init__(self, mongodb, config={}, session=None):
#         super(PipelineStore, self).__init__(mongodb, config, session)
#         coll = self.collections.get('pipelines')
#         if self.debug:
#             coll = '_'.join([coll, str(time_stamp(rounded=True))])
#         self.name = coll
#         self.coll = self.db[coll]
#         self._post_init()

#     def create(self, **kwargs):
#         pipe_rec = Pipeline(**kwargs)
#         pipe_rec.create(**kwargs)

#         try:
#             result = self.coll.insert_one(pipe_rec)
#             result_pipe = self.coll.find_one({'_id': result.inserted_id})
#             result_pipe['token'] = new_token(result_pipe)
#             return filter_dict(result_pipe, pipe_rec.FILTERS)
#         except DuplicateKeyError:
#             raise DuplicatePipelineError('A pipeline with this distinct set of components already exists.')
#         except Exception as exc:
#             raise PipelineUpdateFailure(
#                 'Failed to create pipeline record', exc)

#     def update_pipeline(self, pipeline_uuid, update_token, **kwargs):
#         print('UPDATE PIPELINE')
#         if isinstance(uuid, str):
#             pipeline_uuid = text_uuid_to_binary(pipeline_uuid)

#         pipe_db = self.coll.find_one({'_uuid': pipeline_uuid})
#         if pipe_db is None:
#             raise PipelineUpdateFailure('No pipeline exists with UUID {}. Try create()'.format(pipeline_uuid))

#         try:
#             validate_token(update_token, pipeline_uuid=pipe_db['_uuid'],
#                 salt=pipe_db['_salt'], permissive=False)
#         except InvalidToken as exc:
#             raise PipelineUpdateFailure(exc)

#         # Initialize with database contents
#         pipe_rec = Pipeline(**pipe_db)
#         # Update with body
#         pipe_rec.update(**kwargs)
#         # TODO - return a diff doc containing _informative_ changes
#         # Do the actual database write
#         try:
#             updated_pipe = self.coll.find_one_and_replace(
#                 {'_id': pipe_rec['_id']}, pipe_rec, return_document=ReturnDocument.AFTER)
#             return filter_dict(updated_pipe, pipe_rec.FILTERS)

#         except Exception as exc:
#             raise PipelineUpdateFailure(
#                 'Failed to update pipeline {}'.format(pipeline_uuid), exc)

#     def delete(self, pipeline_uuid, update_token, force=False):
#         """Delete a pipeline by its UUID
#         By default the record is marked as _deleted. If force==True, the
#         record is physically deleted (but this is bad for provenance)."""
#         if force is False:
#             body = {'_deleted': True}
#             return self.update_pipeline(pipeline_uuid, update_token, **body)

#         # We did not branch to the update() action, proceed with hard delete
#         if isinstance(pipeline_uuid, str):
#             pipeline_uuid = text_uuid_to_binary(pipeline_uuid)
#         pipe_rec = self.coll.find_one({'uuid': pipeline_uuid})
#         if pipe_rec is None:
#             raise PipelineUpdateFailure('No pipeline exists with UUID {}. Maybe it was force-deleted?'.format(pipeline_uuid))

#         try:
#             validate_token(update_token, pipeline_uuid=pipe_rec['_uuid'], salt=pipe_rec['_salt'], permissive=False)
#         except InvalidToken as exc:
#             raise PipelineUpdateFailure(exc)

#         try:
#             return self.coll.delete_one({'uuid': pipeline_uuid})
#         except Exception as exc:
#             raise PipelineUpdateFailure(
#                 'Failed to delete pipeline {}'.format(uuid), exc)

#     def undelete(self, pipeline_uuid, update_token):
#         """Un-delete a pipeline by its UUID if it has only been marked as
#         deleted rather than being physically removed from the database."""
#         body = {'_deleted': False}
#         return self.update_pipeline(pipeline_uuid, update_token, **body)

