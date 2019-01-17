import os
import pytest
import sys
import yaml
import json
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
from .fixtures.agave import agave, credentials
import datacatalog
import transitions
from datacatalog.identifiers import abaco, interestinganimal, typeduuid
from .data import pipelinejobs

from datacatalog.managers.pipelinejobs import ManagedPipelineJob
from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance

CWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

@pytest.fixture(scope='session')
def experiment_id():
    return 'experiment.ginkgo.10001'

@pytest.fixture(scope='session')
def sample_id():
    return 'sample.uw_biofab.143209/H1'

@pytest.fixture(scope='session')
def list_job_uuid():
    return '1071269f-b251-5a5f-bec1-6d7f77131f3f'

@pytest.fixture(scope='session')
def client_w_param(mongodb_settings, pipelinejobs_config,
                   agave, pipeline_uuid, experiment_id):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave, experiment_id=experiment_id)

@pytest.fixture(scope='session')
def uninstanced_client_w_param(mongodb_settings, pipelinejobs_config,
                               agave, pipeline_uuid, experiment_id):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave,
                              experiment_id=experiment_id, instanced=False)

def test_pipejob_init_store_list(client_w_param):
    """Smoke test: Can ManagedPipelineJob get through ``init()``
    """
    assert list(client_w_param.stores.keys()) != list()

def test_pipejob_init_archive_path_instanced(client_w_param):
    """Exercises ``instanced=True`` which causes archive path to be
    collision-proof
    """
    assert client_w_param.archive_path.startswith('/products/v2')
    assert client_w_param.archive_path.endswith('Z')

def test_pipejob_init_archive_path_uninstanced(uninstanced_client_w_param):
    """Exercises ``instanced=False`` which causes archive path to be
    completely deterministic
    """
    assert uninstanced_client_w_param.archive_path.startswith('/products/v2')
    assert not uninstanced_client_w_param.archive_path.endswith('Z')

@longrun
def test_pipejob_init_listdir(client_w_param):
    # The listed path is set up for test_agavehelpers and the job_uuid is the
    # from data/tests/pipelinejob/tacbobot.json
    job_uuid = list_job_uuid
    job_path_listing = client_w_param.stores[
        'pipelinejob'].list_job_archive_path(job_uuid)
    assert isinstance(job_path_listing, list)
    assert len(job_path_listing) > 0

def test_pipejob_setup_minimal(client_w_param, pipeline_uuid):
    valid_job_uuid = '1071269f-b251-5a5f-bec1-6d7f77131f3f'

    client_w_param.setup(data={'example_data': 'datadata'})
    assert client_w_param.pipeline_uuid == pipeline_uuid
    assert 'example_data' in client_w_param.data
    assert client_w_param.archive_path.startswith('/products')
    assert client_w_param.uuid == valid_job_uuid

def test_pipejob_agave_uri_from_data(mongodb_settings, pipelinejobs_config,
                                     agave, pipeline_uuid):

    data = {'inputs': ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
                       'agave://data-sd2e-community/products/v1/41e1dec1-2940-5b04-bd9e-54af78f30774/aaf646a5-7c05-5ab3-a144-5563fca6830d/a4609424-508a-555c-9720-5ee3df44e777/whole-shrew-20181207T220030Z/output/output.csv'],
            'parameters': {'p1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs',
                           'p2': '/uploads/456.txt'}}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data, experiment_id='experiment.ginkgo.10001')
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.derived_from) == 3

def test_pipejob_inputs_list(mongodb_settings, pipelinejobs_config,
                             agave, pipeline_uuid):

    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
              'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs']
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs, experiment_id='experiment.ginkgo.10001')
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.derived_from) == 2

def test_pipejob_inputs_resolve(mongodb_settings, pipelinejobs_config,
                                agave, pipeline_uuid):
    # Because both files' lineage resolves to the same experiment, we don't need to send experiment_id
    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
              'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs']
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert '/products/v2/102' in base.archive_path

def test_pipejob_inputs_expt_id(mongodb_settings, pipelinejobs_config,
                                agave, pipeline_uuid):
    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs']
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs, experiment_id='experiment.ginkgo.10001')
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert '/products/v2/102' in base.archive_path

def test_pipejob_data_inputs_resolve(mongodb_settings, pipelinejobs_config,
                                     agave, pipeline_uuid):

    data = {'inputs': {
        'file1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
        'file2': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    }}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.derived_from) == 2
    # assert base.archive_path is None

def test_pipejob_data_inputs_list_resolve(mongodb_settings, pipelinejobs_config, agave, pipeline_uuid):

    data = {'inputs': [
        'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs',
        '/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    ]}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the first two inputs resolvable since the list context expects fully-qualified URIs
    assert len(base.derived_from) == 2
    # assert base.archive_path is None

def test_pipejob_data_inputs_refs_resolve(mongodb_settings, pipelinejobs_config, agave, pipeline_uuid):

    data = {'inputs': [
        'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs',
        'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_WT/MG1655_WT.fa.ann'
    ]}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the first two inputs resolvable since the list context expects fully-qualified URIs
    assert len(base.derived_from) == 3
    # assert base.archive_path is None

def test_pipejob_data_params_refs_resolve(mongodb_settings, pipelinejobs_config, agave, pipeline_uuid):

    data = {'parameters': {'structure': 'https://www.rcsb.org/structure/6N0V',
                           'protein': 'https://www.uniprot.org/uniprot/G0S6G2'}}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # ^^ These references should be present in the database if test_stores_reference has been run
    assert len(base.derived_from) == 2

def test_pipejob_data_parameters_resolve(mongodb_settings, pipelinejobs_config,
                                         agave, pipeline_uuid):

    data = {'parameters': {
        'param1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
        'param2': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    }}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.derived_from) == 2

def test_pipejob_data_input_parameters_resolve(mongodb_settings, pipelinejobs_config,
                                               agave, pipeline_uuid):

    data = {'inputs': {
        'file1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs'},
        'parameters': {
        'param1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
        'param2': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    }}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.derived_from) == 2

def test_pipeinstance_init(mongodb_settings, agave):
    """Verify that we can instantiate an instance of a known job without a bunch of boilerplate"""
    job_uuid = '107a6c4a-f354-53d6-b97d-2c497b9b352e'
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)

    assert base.archive_path.startswith('/products/v2/102')
    assert len(base.derived_from) > 0
    assert len(base.generated_by) > 0
    assert len(base.pipeline_uuid) is not None


# TODO Rewrite these tests to use new signature for ManagedPipelineJob


# def test_pipejob_setup_instanced(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, instanced=True)
#     base.setup(data={'example_data': 'datadata'})
#     assert base.archive_path.endswith('Z')

# def test_pipejob_setup_not_instanced(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, instanced=False)
#     base.setup(data={'example_data': 'datadata'})
#     assert not base.archive_path.endswith('Z')

# def test_pipejob_callback(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     assert base.callback.startswith('https://')

# def test_pipejob_run(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})

# def test_pipejob_run_resource(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     base.resource(data={'this_data': 'is from the "resource" event'})

# def test_pipejob_update(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     base.update(data={'this_data': 'is from an update event'})

# def test_pipejob_run_update_resource(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     base.update(data={'this_data': 'is from an update event'})
#     base.resource(data={'this_data': 'is from the "resource" event'})

# def test_pipejob_fail(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     base.update(data={'this_data': 'is from an update event'})
#     base.fail(data={'this_data': 'is from a fail event'})

# def test_pipejob_fail_fsm_enforce(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     base.update(data={'this_data': 'is from an update event'})
#     base.fail(data={'this_data': 'is from a fail event'})
#     with pytest.raises(transitions.core.MachineError):
#         base.update(data={'this_data': 'is from an update event'})

# def test_pipejob_finish(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     base.update(data={'this_data': 'is from an update event'})
#     base.finish(data={'this_data': 'is from a finish event'})

# def test_pipejob_no_finish_without_run(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id)
#     base.setup(data={'example_data': 'datadata'})
#     with pytest.raises(transitions.core.MachineError):
#         base.finish(data={'this_data': 'is from a finish event'})

# def test_pipejob_mgr_params(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, actor_id, session):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=actor_id, session=session)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     assert base.session == session
#     assert base.job['agent'].endswith(actor_id)

# def test_pipejob_task(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, actor_id, exec_id, session):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=actor_id, task=exec_id, session=session)
#     base.setup(data={'example_data': 'datadata'})
#     assert base.session == session
#     assert base.job['task'].endswith(exec_id)

# def test_pipejob_agave_agent_task(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, agave_app_id, agave_job_id, session):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=agave_app_id, task=agave_job_id, session=session)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     assert base.job['agent'].endswith(agave_app_id)
#     assert base.job['task'].endswith(agave_job_id)

# def test_pipejob_custom_archive_path(mongodb_settings, manager_id, nonce, pipeline_uuid, experiment_id, sample_id, actor_id, session):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid, experiment_id=experiment_id, sample_id=sample_id, agent=actor_id, session=session, archive_path='/archives')
#     base.setup(data={'example_data': 'datadata'})
#     assert base.job['archive_path'] == '/archives'

# @pytest.mark.parametrize("param,value,success", [('experiment_id', 'experiment.uw_biofab.17987', True),
#                                                  ('sample_id', 'sample.uw_biofab.143209/H1', True),
#                                                  ('measurement_id', 'measurement.uw_biofab.92242', True),
#                                                  ('agent', '6e87V7aqrX646', False)])
# def test_pipejob_one_of_params(mongodb_settings, manager_id, nonce, param, value, success, pipeline_uuid):
#     doc = {'pipeline_uuid': pipeline_uuid, param: value}
#     if success is True:
#         mjob = ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
#         mjob.setup()
#         assert mjob.pipeline_uuid == doc['pipeline_uuid']
#     else:
#         with pytest.raises(store.ManagedPipelineJobError):
#             mjob = ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
#             mjob.setup()

# @delete
# def test_pipejob_no_cancel_after_run(mongodb_settings, manager_id, nonce, pipeline_uuid):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid)
#     base.setup(data={'example_data': 'datadata'})
#     base.run(data={'this_data': 'is from the "run" event'})
#     with pytest.raises(ManagedPipelineJobError):
#         base.cancel()

# @delete
# def test_pipejob_cancel(mongodb_settings, manager_id, nonce, pipeline_uuid):
#     base = ManagedPipelineJob(mongodb_settings, manager_id, nonce, pipeline_uuid=pipeline_uuid)
#     base.setup(data={'example_data': 'datadata'})
#     base.cancel()

# def test_pipejob_create_jobs_kwargs(mongodb_settings, manager_id, nonce):
#     for struct in pipelinejobs.get_jobs():
#         doc = struct['data']
#         # pprint(doc)
#         if struct['valid'] is True:
#             mjob = ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
#             mjob.setup()
#             assert mjob.uuid == struct['uuid']
#         else:
#             with pytest.raises(store.ManagedPipelineJobError):
#                 mjob = ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
#                 mjob.setup()

# @delete
# def test_pipejob_delete_jobs_kwargs(mongodb_settings, manager_id, nonce):
#     for struct in pipelinejobs.get_jobs():
#         doc = struct['data']
#         if struct['valid'] is True:
#             mjob = ManagedPipelineJob(mongodb_settings, manager_id, nonce, **doc)
#             mjob.setup()
#             assert mjob.uuid == struct['uuid']
#             mjob.cancel()

# @longrun
# def test_pipesinstance_index_archive_path(mongodb_settings, agave):
#     job_uuid = '1079f67e-0ef6-52fe-b4e9-d77875573860'
#     filters = ['sample\.uw_biofab\.141715', 'sample-uw_biofab-141715']
#     level = "1"
#     base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
#     assert len(base.index_archive_path(filters=filters, processing_level=level)) > 0
