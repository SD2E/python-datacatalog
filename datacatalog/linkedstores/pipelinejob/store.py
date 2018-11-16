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
from pprint import pprint

from ... import identifiers
from ...dicthelpers import data_merge
from ...pathmappings import normalize, abspath
from ..basestore import BaseStore, CatalogUpdateFailure, HeritableDocumentSchema, SoftDelete
from ..basestore import validate_token

from .exceptions import JobCreateFailure, JobUpdateFailure, DuplicateJobError, UnknownPipeline, UnknownJob
from .schema import JobDocument, HistoryEventDocument
from .job import PipelineJob

class PipelineJobStore(SoftDelete, BaseStore):
    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(PipelineJobStore, self).__init__(mongodb, config, session)
        # setup based on schema extended properties
        schema = JobDocument(**kwargs)
        super(PipelineJobStore, self).update_attrs(schema)
        # setattr(self, 'name', schema.get_collection())
        # setattr(self, 'schema', schema.to_dict())
        # setattr(self, 'identifiers', schema.get_identifiers())
        # setattr(self, 'uuid_type', schema.get_uuid_type())
        # setattr(self, 'uuid_fields', schema.get_uuid_fields())
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

class StoreInterface(PipelineJobStore):
    pass
