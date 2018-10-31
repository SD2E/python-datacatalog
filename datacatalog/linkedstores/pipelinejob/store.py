
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *

import os
import sys
import uuid
from pprint import pprint

from ..basestore import time_stamp, msec_precision, debug_mode, validate_token
from ..basestore import BaseStore, CatalogUpdateFailure, DocumentSchema, HeritableDocumentSchema, SoftDelete
from .. import identifiers

from .exceptions import JobCreateFailure, JobUpdateFailure, DuplicateJobError, UnknownPipeline, UnknownJob
from .schema import JobDocument, HistoryEventDocument
from .job import PipelineJob

class PipelineJobStore(SoftDelete, BaseStore):
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(PipelineJobStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = JobDocument(**kwargs)
        setattr(self, 'name', schema.get_collection())
        setattr(self, 'schema', schema.to_dict())
        setattr(self, 'identifiers', schema.get_identifiers())
        setattr(self, 'uuid_type', schema.get_uuid_type())
        setattr(self, 'uuid_fields', schema.get_uuid_fields())
        self.setup()
        setattr(self, 'pipes_coll', self.db['pipelines'])

    def create(self, job_document, **kwargs):

        # Must refer to an existing pipeline
        self.validate_pipeline_uuid(job_document.get('pipeline_uuid'))

        # Must refer to a valid (but not verified) abaco actorId
        try:
            identifiers.abaco_hashid.validate(job_document.get('actor_id'))
        except Exception:
            pass

        if 'uuid' not in job_document:
            job_document['uuid'] = self.get_typed_uuid(job_document)
        # Job object contains schema plus logic to manage event lifecycle
        # Can be materialized from a passed document or by database record
        pipe_job_document = PipelineJob(job_document).new()
        return self.add_update_document(pipe_job_document.to_dict())

    def handle(self, event_document, token=None, data=None, **kwargs):
        # This is a special method that takes event documents
        # and modifies the job state/history
        try:
            job_uuid = event_document.get('uuid')
        except KeyError:
            raise JobUpdateFailure('Cannot process an event without a job UUID')
        passed_token = event_document.get('token', token)
        db_record = self.find_one_by_uuid(job_uuid)
        # Token must validate
        validate_token(passed_token, db_record['_salt'], self.get_token_fields(db_record))
        db_job = PipelineJob(db_record).handle(event_document)

        # try:
        #     db_job.handle(event_document)
        # except Exception as exc:
        #     raise JobUpdateFailure('Failed to handle event', exc)
        return self.add_update_document(db_job.to_dict())

    def delete(self, job_uuid, token, soft=False):
        # Special kind of event
        pass

    def history(self, job_uuid, limit=None, skip=None):
        pass

# class JobStore(BaseStore):
#     """Manages creation and management of datacatalog.jobs records and states"""

#     def __init__(self, mongodb, config, pipeline_store=None, session=None):
#         super(JobStore, self).__init__(mongodb, config, session)
#         coll = self.collections.get('jobs')
#         coll_pipes = self.collections.get('pipelines')
#         if self.debug:
#             ts = time_stamp(rounded=True)
#             coll = '_'.join([coll, str(ts)])
#             coll_pipes = '_'.join([coll_pipes, str(ts)])
#         self.name = coll
#         self.coll = self.db[coll]
#         self.coll_db = self.db[coll_pipes]
#         self._post_init()
#         self.CREATE_OPTIONAL_KEYS = [
#             'data', 'session', 'actor_id']
#         self.EVENT_OPTIONAL_KEYS = ['data']

#     def create(self, pipeline_uuid, archive_path, **kwargs):
#         """Create and return a new job instance
#         Parameters:
#         pipeline_uuid:uuid5 - valid db.pipelines.uuid
#         archive_path:str - job archive path relative to products store
#         data:dict - JSON serializable dict describing parameterization of the job
#         Arguments:
#         session:str - correlation string (optional)
#         binary_uuid:bool - whether to return a text or BSON binary UUID
#         Returns:
#         A jobs.uuid referring to the job in the data catalog
#         """
#         DEFAULTS = {'data': {},
#                     'session': None,
#                     'actor_id': None,
#                     'execution_id': None}
#         # Validate pipeline_uuid
#         self.validate_pipeline_id(pipeline_uuid)
#         # Validate actor_id and execution_id
#         # In the future, decide if jobs MUST be created by Actors. If not
#         # then the data model should migrate to using to 'agent' and 'task'
#         # which are the terms used in the Log Aggregation framework
#         identifiers.abaco_hashid.validate(kwargs['actor_id'])
#         try:
#             identifiers.abaco_hashid.validate(kwargs['execution_id'])
#         except Exception:
#             pass
#         job_data = data_merge(DEFAULTS, kwargs)
#         job_data['path'] = archive_path
#         job_data['_deleted'] = True
#         # job definition gets validated in DataCatalogJob
#         new_job = DataCatalogJob(pipeline_uuid, job_data)
#         print(new_job)
#         try:
#             result = self.coll.insert_one(new_job.as_dict())
#             new_job = self.coll.find_one({'_id': result.inserted_id})
#             # inject a validation token into response
#             new_job['token'] = new_token(new_job)

#             # TODO factor this out into a general filter function
#             try:
#                 new_job.pop('_salt')
#             except Exception:
#                 pass
#             return new_job
#         except Exception as exc:
#             raise JobCreateFailure('Failed to create job for pipeline {}'.format(pipeline_uuid), exc)

#     def handle_event(self, job_uuid, event, token, **kwargs):
#         """Accept and process a job state-transition event
#         Parameters:
#         job_uuid:uuid5 - identifier for the job that is recieving an event
#         event_name:str - event to be processed (Must validate to JobStateMachine.events)
#         token:str - validation token issued when the job was created
#         Arguments:
#         data:dict - optional dict to pass to JobStateMachine event handler
#         permissive:bool - ignore state and other Exceptions
#         Returns:
#         Boolean for successful handling of the event
#         """
#         DEFAULTS = {'data': {}}
#         # Validate job_uuid
#         # if isinstance(job_uuid, str):
#         #     job_uuid = identifiers.datacatalog_uuid.text_uuid_to_binary(job_uuid)
#         details_data = data_merge(DEFAULTS, kwargs)
#         db_job = None
#         try:
#             job_rec = self.coll.find_one({'_uuid': job_uuid})
#             if job_rec is None:
#                 raise JobUpdateFailure('No job found with that UUID')

#             # token is job-specific
#             try:
#                 validate_token(token, pipeline_uuid=job_rec['_pipeline_uuid'], job_uuid=job_rec['_uuid'], salt=job_rec['_salt'], permissive=False)
#             except InvalidToken as exc:
#                 raise JobUpdateFailure(exc)

#             # Materialize out the job from database and handle the event with its FSM
#             db_job = DataCatalogJob(job_rec['pipeline_uuid'], job_doc=job_rec)
#             db_job.handle(event, opts=details_data['data'])
#             db_job = db_job.as_dict()
#         except Exception as exc:
#             raise JobUpdateFailure('Failed to change the job state', exc)
#         try:
#             updated_job = self.coll.find_one_and_replace({'uuid': db_job.get('uuid')}, db_job,
#                                                          return_document=ReturnDocument.AFTER)

#             # TODO factor this out into a general filter function
#             try:
#                 updated_job.pop('_salt')
#             except Exception:
#                 pass
#             return updated_job
#         except Exception as exc:
#             raise JobUpdateFailure('Failed up write job to database', exc)

#     def delete_job(self, job_uuid, force=False):
#         pass

#     def __validate_job_def(self, job_def):
#         # Noop for now
#         return True

    def validate_pipeline_uuid(self, pipeline_uuid):
        if self.debug_mode() is True:
            return True
        else:
            try:
                pipe = self.pipes_coll.find_one({'uuid': pipeline_uuid})
                if pipe is not None:
                    return True
                else:
                    raise UnknownPipeline(
                        'No pipeline exists with UUID {}'.format(str(pipeline_uuid)))
            except Exception as exc:
                raise Exception('Failed to validate pipeline UUID', exc)