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
from ..basestore import LinkedStore, CatalogUpdateFailure, HeritableDocumentSchema, SoftDelete
from ..basestore import get_token, validate_token

from .exceptions import JobCreateFailure, JobUpdateFailure, DuplicateJobError, UnknownPipeline, UnknownJob
from .schema import JobDocument, HistoryEventDocument
from .job import PipelineJob, PipelineJobError

class PipelineJobStore(SoftDelete, LinkedStore):
    NEVER_INDEX_FIELDS = ('data')
    """Fields that should never be indexed"""

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(PipelineJobStore, self).__init__(mongodb, config, session)

        # setup based on schema extended properties
        schema = JobDocument(**kwargs)
        super(PipelineJobStore, self).update_attrs(schema)
        self._enforce_auth = False

        self.setup()
        # Extend Store so it can validate the pipeline UUID
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
            job_document['uuid'] = self.get_typeduuid(job_document)
        # Job object contains schema plus logic to manage event lifecycle
        # Can be materialized from a passed document or by database record
        pipe_job_document = PipelineJob(job_document).new()
        return self.add_update_document(pipe_job_document.to_dict())

    def handle(self, event_document, token=None, data=None, **kwargs):
        # This is a special method that takes event documents
        # and modifies the job state/history
        job_uuid = None
        try:
            job_uuid = event_document.get('uuid')
        except KeyError:
            raise JobUpdateFailure('Cannot process an event without a job UUID')

        db_record = self.find_one_by_uuid(job_uuid)
        if db_record is None:
            raise UnknownJob('{} is not a valid job ID'.format(job_uuid))

        passed_token = event_document.get('token', token)
        # Token must validate
        validate_token(passed_token, db_record['_salt'], self.get_token_fields(db_record))
        db_job = PipelineJob(db_record).handle(event_document)
        return self.add_update_document(db_job.to_dict())

    def delete(self, job_uuid, token, soft=False):
        # Special kind of event
        return self.delete_document(job_uuid, token, soft)

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

    # # TODO: Figure out how to patch in Pipeline.id
    # def get_typeduuid(self, payload, binary=False):
    #     """Pipeline-specific method for getting a UUID

    #     Args:
    #         payload (object): A list or dict containing the pipeline definition

    #     Returns:
    #         str: A UUID for this Pipeline
    #     """
    #     # print('PAYLOAD', payload)
    #     uuid_els = list()
    #     uuid_els.append(payload.get('pipeline_uuid', 'pipeline.id'))

    #     cplist = payload.get('components', [])
    #     spdoc = SerializedPipeline(cplist).to_json()
    #     uuid_els.append(spdoc)
    #     uuid_target = ':'.join(uuid_els)
    #     # print('UUID_TARGET', uuid_target)
    #     return super(PipelineStore, self).get_typeduuid(uuid_target, binary=binary)


class StoreInterface(PipelineJobStore):
    pass
