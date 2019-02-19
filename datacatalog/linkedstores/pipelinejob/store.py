import base64
import inspect
import json
import os
import sys
from pprint import pprint
import random
import string
import tempfile

from ... import identifiers
from ...constants import Constants
from ...dicthelpers import data_merge
from ...pathmappings import normalize, abspath
from ..basestore import LinkedStore, HeritableDocumentSchema
from ..basestore import CatalogUpdateFailure
from ..basestore import SoftDelete, AgaveClient
from ..basestore import get_token, validate_token, validate_admin_token

from .exceptions import JobError, JobCreateFailure, JobUpdateFailure, \
    DuplicateJobError, UnknownPipeline, UnknownJob
from .schema import JobDocument, HistoryEventDocument
from .job import PipelineJob, PipelineJobError
from .graphfsm import render_graph, build_graph

DEFAULT_LINK_FIELDS = ('child_of', 'derived_from', 'generated_by', 'acted_on', 'acted_using')

class PipelineJobStore(AgaveClient, SoftDelete, LinkedStore):
    NEVER_INDEX_FIELDS = ('data')
    """Fields that should never be indexed"""

    def __init__(self, mongodb, config={}, session=None, agave=None, **kwargs):
        super(PipelineJobStore, self).__init__(mongodb, config, session, agave)
        # setup based on schema extended properties
        schema = JobDocument(**kwargs)
        super(PipelineJobStore, self).update_attrs(schema)
        self._enforce_auth = True

        self.setup()
        # Extend Store so it can validate the pipeline UUID
        setattr(self, 'pipes_coll', self.db['pipelines'])

    def uuid_from_properties(self, job_document, **kwargs):
        self.validate_pipeline_uuid(job_document.get('pipeline_uuid'))
        # Must refer to a valid (but not verified) abaco actorId
        try:
            identifiers.abaco_hashid.validate(job_document.get('actor_id'))
        except Exception:
            pass
        return job_document.get('uuid', self.get_typeduuid(job_document))

    def create(self, job_document, **kwargs):

        job_uuid = self.uuid_from_properties(job_document, **kwargs)
        job_document['uuid'] = job_uuid
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

        # Allow handle() to accept token as an argument or as a key
        # in the event_document
        passed_token = event_document.get('token', token)

        # Token must validate
        # TODO - Extend validate_token to honor one or more admin tokens set in env
        validate_token(passed_token, db_record['_salt'], self.get_token_fields(db_record))
        db_job = PipelineJob(db_record).handle(event_document)
        return self.add_update_document(db_job.to_dict())

    def delete(self, job_uuid, token, soft=False):
        # Special kind of event
        validate_admin_token(token, permissive=False)
        return self.delete_document(job_uuid, token=token, soft=soft)

    def history(self, job_uuid, limit=None, skip=None):
        pass

    def validate_pipeline_uuid(self, pipeline_uuid):
        try:
            pipe = self.pipes_coll.find_one({'uuid': pipeline_uuid})
            if pipe is not None:
                return True
            else:
                raise UnknownPipeline(
                    'No pipeline exists with UUID {}'.format(str(pipeline_uuid)))
        except Exception as exc:
            raise Exception('Failed to validate pipeline UUID', exc)

    def list_job_archive_path(self, job_uuid, recurse=True, directories=False, **kwargs):
        """Returns contents of a job's archive_path

        Args:
            job_uuid (str): UUID of the job

        Notes:
            PipelineJobStore must be initialized with a valid Agave API client

        Returns:
            list: Agave-canonical absolute filenames in job.archive_path
        """

        db_record = self.find_one_by_uuid(job_uuid)
        if db_record is None:
            raise UnknownJob('{} is not a valid job ID'.format(job_uuid))

        dir_listing = self._helper.listdir(
            db_record['archive_path'],
            recurse=recurse,
            storage_system=db_record.get('archive_system',
                                         Constants.CATALOG_AGAVE_STORAGE_SYSTEM),
            directories=False)

        return dir_listing

    def fsm_state_png(self, uuid):
        try:
            job = self.find_one_by_uuid(uuid)
            if job is not None:
                events = [hist['name'] for hist in job['history']]
                title = 'job:' + uuid
                graph = build_graph(job['state'], title, events)
                tmpname = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                tmpfp = os.path.join(tempfile.gettempdir(), tmpname)
                graph.draw(tmpfp, format='png', prog='dot')
                encoded = base64.b64encode(open(tmpfp, "rb").read())
                os.unlink(tmpfp)
                return encoded
            else:
                raise ValueError('Unable to retrieve job {}'.format(uuid))
        except Exception as exc:
            raise JobError('Failed to get_graph', exc)

class StoreInterface(PipelineJobStore):
    pass
