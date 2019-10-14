import pytest
import os
from datacatalog import managers
from .data import issues

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

def test_issue15_create_large_job(mongodb_settings, agave,
                                  pipelinejobs_config, admin_token):
    job_def = issues.issue15.job_dict
    pconfig = pipelinejobs_config
    pconfig['pipeline_uuid'] = job_def['pipeline_uuid']

    mpj = managers.pipelinejobs.ManagedPipelineJob(
        mongodb_settings, pconfig, agave=agave, **job_def)

    try:
        mpj.reset(token=admin_token).ready(token=admin_token)
    except Exception:
        pass

    mpj.setup()
    mpj.run()
    mpj.reset(token=admin_token)

@pytest.mark.longrun
@pytest.mark.parametrize("filename", ['new-sample-id-scheme.json'])
def test_pr80_sample_id_refactor_load_sampleset(mongodb_settings, filename):
    DATA_DIR = os.path.join(HERE, 'data/sampleset')
    jsonpath = os.path.join(DATA_DIR, filename)
    db = managers.sampleset.SampleSetProcessor(
        mongodb_settings, samples_file=jsonpath).setup()
    dbp = db.process(strategy='merge')
    assert dbp is True
