import os
import pytest
import sys
import yaml
import json
import inspect
import warnings
from pprint import pprint

from . import longrun, delete
from .fixtures import mongodb_settings, agave, credentials, admin_token, admin_key

import datacatalog
import traceback
import transitions
from datacatalog.identifiers import abaco, interestinganimal, typeduuid

from .data import issues

def test_issue15_create_large_job(mongodb_settings, agave, pipelinejobs_config, admin_token):
    job_def = issues.issue15.job_dict
    pconfig = pipelinejobs_config
    pconfig['pipeline_uuid'] = job_def['pipeline_uuid']

    from datacatalog.managers.pipelinejobs import (ManagedPipelineJob,
                                                   ManagedPipelineJobError)
    mpj = ManagedPipelineJob(mongodb_settings, pconfig, agave=agave, **job_def)

    try:
        mpj.reset(token=admin_token).ready(token=admin_token)
    except Exception:
        pass

    mpj.setup()
    mpj.run()
    mpj.reset(token=admin_token)
