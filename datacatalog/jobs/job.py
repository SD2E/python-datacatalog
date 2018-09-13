import copy
import inspect
import json
import os
from pprint import pprint
from attrdict import AttrDict
from jsonschema import validate, FormatChecker
from jsonschema import ValidationError
from .fsm import JobStateMachine
from ..identifiers.datacatalog_uuid import random_uuid5, text_uuid_to_binary
from .utils import params_to_document, params_document_to_uuid
from ..constants import UUID_NAMESPACE
import uuid
from bson.binary import Binary, UUID_SUBTYPE, OLD_UUID_SUBTYPE

class formatChecker(FormatChecker):
    def __init__(self):
        FormatChecker.__init__(self)

class Job(AttrDict):
    pass

class DataCatalogJob(object):
    def __init__(self, pipeline_uuid, job_def_dict={}):

        # self.uuid = random_uuid5()
        self.uuid = params_document_to_uuid(params_to_document(job_def_dict))
        self._document = job_def_dict
        self.job = None
        if isinstance(pipeline_uuid, str):
            self.pipeline_uuid = text_uuid_to_binary(pipeline_uuid)
        else:
            self.pipeline_uuid = pipeline_uuid

        # HERE = os.path.abspath(inspect.getfile(self.__class__))
        # PARENT = os.path.dirname(HERE)
        # schema_path = os.path.join(PARENT, 'schema.json')
        # validation_schema = {}
        # try:
        #     with open(schema_path) as schema:
        #         validation_schema = json.loads(schema.read())
        # except Exception as e:
        #     raise ValidationError('Failed to load job JSON schema', e)
        # # Validate the incoming job definition before setting up a FSM
        # try:
        #     validate(self._document, validation_schema,
        #              format_checker=formatChecker())
        # except Exception as exc:
        #     raise ValidationError(exc)
        self.job = JobStateMachine(jobdef=job_def_dict)

    def handle(self, event, opts={}):
        self.job.handle(event, opts=opts)
        return self

    def history(self):
        return self.job.history()

    def as_dict(self):
        pr = {}
        for name in dir(self):
            if name != 'job':
                value = getattr(self, name)
                if not name.startswith('__') and not inspect.ismethod(value):
                    pr[name] = value
        pr['job'] = self.job.data
        return Job(pr)


# pipeline_uuid: pipeline.uuid
# _document: original job document
# job:
#     history:
#         - state: < datetime.datetime >
#     data: < dict >
# uuid: job.uuid(generated)
# jsonschema
