import os
import pytest
import sys
import yaml
import json
import inspect
from pprint import pprint
from . import longrun, delete
from .fixtures.mongodb import mongodb_settings, mongodb_authn
from .fixtures.agave import agave, credentials
import datacatalog
import traceback
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
def job_data():
    data_obj = {
        'inputs': {
            'file1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
            'ref1': 'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_WT/MG1655_WT.fa.ann'},
        'parameters': {
            'param2': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    }}
    return data_obj

@pytest.fixture(scope='session')
def client_w_param_data(mongodb_settings, pipelinejobs_config,
                   agave, pipeline_uuid, experiment_id, job_data):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave,
                              experiment_id=experiment_id,
                              data=job_data)

@pytest.fixture(scope='session')
def client_w_archive_path(mongodb_settings, pipelinejobs_config,
                   agave, pipeline_uuid):
    return ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave, archive_path='/products/v2/test123')

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

def test_pipejob_init_archive_path_custom(mongodb_settings, pipelinejobs_config,
                   agave, pipeline_uuid):
    """Exercises ``instanced=True`` which causes archive path to be
    collision-proof
    """
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config,
                              agave=agave, archive_path='/products/v2/test123')
    assert base.archive_path.startswith('/products/v2')
    assert base.archive_path.endswith('test123')

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
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.acts_on) == 3

def test_pipejob_inputs_list(mongodb_settings, pipelinejobs_config,
                             agave, pipeline_uuid):

    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
              'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs']
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs, experiment_id='experiment.ginkgo.10001')
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    # The experiment_id will resolve as well
    assert len(base.acts_on) == 2

# def test_pipejob_inputs_resolve(mongodb_settings, pipelinejobs_config,
#                                 agave, pipeline_uuid):
#     # Because both files' lineage resolves to the same experiment, we don't need to send experiment_id
#     inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
#               'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs']
#     base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs)
#     # Only the two inputs and the first parameter have resolvable UUID in the test data set
#     assert '/products/v2/102' in base.archive_path

def test_pipejob_inputs_no_link_or_data(mongodb_settings, pipelinejobs_config,
                                agave, pipeline_uuid):
    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs']
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.child_of) > 0
    # The hashid value for measurement.tacc.0x00000000, the default
    assert '5pQxBkRrRe2GEPOWWZBq4LNQ' in base._archive_path_els
    # The hashid value for an empty "data" dictionary
    assert 'PAVpwrObxp5YjYRvrJOd5yVp' in base._archive_path_els
    # Pipeline ID is exposed in the path because there is a 1:1 mapping
    assert '/106' in base.archive_path

@pytest.mark.parametrize("recid,raises_exception", [
    ("experiment.tacc.10001", False),
    (["experiment.tacc.10001"], False),
    (["102e95e6-67a8-5a06-9484-3131c6907890"], False),
    ("102e95e6-67a8-5a06-9484-3131c6907890", False),
    (["102e95e6-67a8-5a06-9484-3131c6907890", "experiment.tacc.10001"], False),
])
def test_pipejob_inputs_expt_id(mongodb_settings, pipelinejobs_config,
                                agave, pipeline_uuid, recid, raises_exception):
    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs']
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs, experiment_id=recid)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.child_of) > 0
    # The hashid value for measurement.tacc.0x00000000, the default
    # Should NOT be present if we resolve measurements
    assert '5pQxBkRrRe2GEPOWWZBq4LNQ' not in base._archive_path_els
    assert '/106' in base.archive_path

@pytest.mark.parametrize("recid,raises_exception", [
    ("sample.tacc.20001", False),
    (["sample.tacc.20001"], False),
    (["sample.tacc.20001", "sample.tacc.20002"], False),
    (["103246e1-bcdf-5b6e-a8dc-4c7e81b91141"], False),
    ("103246e1-bcdf-5b6e-a8dc-4c7e81b91141", False)
])
def test_pipejob_inputs_sample_id(mongodb_settings, pipelinejobs_config,
                                agave, pipeline_uuid, recid, raises_exception):
    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs']

    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs, sample_id=recid)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.child_of) > 0
    # The hashid value for measurement.tacc.0x00000000, the default
    # Should NOT be present if we resolve measurements
    assert '5pQxBkRrRe2GEPOWWZBq4LNQ' not in base._archive_path_els
    assert '/106' in base.archive_path

@pytest.mark.parametrize("recid,raises_exception", [
    ("measurement.tacc.0xDEADBEEF", False),
    (["measurement.tacc.0xDEADBEEF"], False),
    (["measurement.tacc.0xDEADBEEF", "measurement.tacc.0xDEADBEF0", "measurement.tacc.0xDEADBEF1"], False),
    (["1041ab3f-5221-5c79-8781-8838dfb6eef9"], False),
    ("1041ab3f-5221-5c79-8781-8838dfb6eef9", False)
])
def test_pipejob_inputs_meas_id(mongodb_settings, pipelinejobs_config,
                                agave, pipeline_uuid, recid, raises_exception):
    inputs = ['agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.0003_4.fcs']

    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, inputs=inputs, measurement_id=recid)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.child_of) > 0
    # The hashid value for measurement.tacc.0x00000000, the default
    # Should NOT be present if we resolve measurements
    assert '5pQxBkRrRe2GEPOWWZBq4LNQ' not in base._archive_path_els
    assert '/106' in base.archive_path

def test_pipejob_data_inputs_resolve(mongodb_settings, pipelinejobs_config,
                                     agave, pipeline_uuid):

    data = {'inputs': {
        'file1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
        'file2': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    }}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.acts_on) == 2
    # assert base.archive_path is None

def test_pipejob_data_inputs_list_resolve(mongodb_settings, pipelinejobs_config, agave, pipeline_uuid):

    data = {'inputs': [
        'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs',
        '/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    ]}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the first two inputs resolvable since the list context expects fully-qualified URIs
    assert len(base.acts_on) == 2
    # assert base.archive_path is None

def test_pipejob_data_inputs_refs_resolve(mongodb_settings, pipelinejobs_config, agave, pipeline_uuid):

    data = {'inputs': [
        'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs', 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs',
        'agave://data-sd2e-community/reference/novel_chassis/uma_refs/MG1655_WT/MG1655_WT.fa.ann'
    ]}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the first two inputs resolvable since the list context expects fully-qualified URIs
    assert len(base.acts_on) == 2
    assert len(base.acts_using) == 1

    # assert base.archive_path is None

def test_pipejob_data_params_refs_resolve(mongodb_settings, pipelinejobs_config, agave, pipeline_uuid):

    data = {'parameters': {'structure': 'https://www.rcsb.org/structure/6N0V',
                           'protein': 'https://www.uniprot.org/uniprot/G0S6G2'}}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # ^^ These references should be present in the database if test_stores_reference has been run
    assert len(base.acts_on) == 0
    assert len(base.acts_using) == 2

def test_pipejob_data_parameters_resolve(mongodb_settings, pipelinejobs_config,
                                         agave, pipeline_uuid):

    data = {'parameters': {
        'param1': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmggea748b_r1bsun4yb67e7/wt-control-1_0.00015_2.fcs',
        'param2': 'agave://data-sd2e-community/uploads/transcriptic/201808/yeast_gates/r1bsmgdayg2yq_r1bsu7tb7bsuk/6389_0.0003_4.fcs'
    }}
    base = ManagedPipelineJob(mongodb_settings, pipelinejobs_config, agave=agave, data=data)
    # Only the two inputs and the first parameter have resolvable UUID in the test data set
    assert len(base.acts_on) == 2

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
    assert len(base.acts_on) == 2

def test_pipeinstance_init(mongodb_settings, agave):
    """Verify that we can instantiate an instance of a known job without a bunch of boilerplate"""
    job_uuid = '1071269f-b251-5a5f-bec1-6d7f77131f3f'
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
    assert base.archive_path.startswith('/products/v2/106')
    assert len(base.child_of) > 0
    assert len(base.pipeline_uuid) is not None
    assert 'run' in dir(base)

# def test_pipeinstance_event_fn(mongodb_settings, agave):
#     """Verify that we can instantiate an instance of a known job without a bunch of boilerplate"""
#     job_uuid = '1071269f-b251-5a5f-bec1-6d7f77131f3f'
#     base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
#     # pprint(inspect.getmembers(base))
#     print(inspect.getsource(base.run))
#     raise SystemError()
#     resp = base.run()
#     assert 'uuid' in resp

# TODO Rewrite these tests to use new signature for ManagedPipelineJob

def test_pipejob_init_callback(client_w_param_data):
    """Check that callback can be materialized but not until after setup()
    """
    client_w_param_data.setup()
    assert client_w_param_data.callback.startswith('https://')

def test_pipejob_event_run(client_w_param_data):
    """Check that run() can happen now
    """
    resp = client_w_param_data.run(data={'this_data': 'is from the "run" event'})
    assert resp['state'] == 'RUNNING'

def test_pipejob_event_update(client_w_param_data):
    """Check that update() can happen now
    """
    resp = client_w_param_data.run(data={'this_data': 'is from the "update" event'})
    assert resp['state'] == 'RUNNING'

def test_pipejob_event_resource(client_w_param_data):
    """Check that resource() can happen now
    """
    resp = client_w_param_data.resource(data={'this_data': 'is from the "resource" event'})
    assert resp['state'] == 'RUNNING'

def test_pipejob_event_finish(client_w_param_data):
    """Check that finish() can happen now
    """
    resp = client_w_param_data.finish(data={'this_data': 'is from the "finish" event'})
    assert resp['state'] == 'FINISHED'

def test_pipejob_event_index(client_w_param_data):
    """Check that index() can happen now
    """
    resp = client_w_param_data.index(data={'this_data': 'is from the "index" event'})
    assert resp['state'] == 'INDEXING'

def test_pipejob_event_indexed(client_w_param_data):
    """Check that indexed() can happen now
    """
    resp = client_w_param_data.indexed(data={'this_data': 'is from the "indexed" event'})
    assert resp['state'] == 'FINISHED'

@longrun
def test_pipesinst_index_w_filters(mongodb_settings, agave):
    """Indexing with filters returns job.archive_path x filters
    """
    # This job is generated in the database by test_109#test_job_create
    # Its archive_patterns = ['ansible.png']
    job_uuid = '10797ce0-c130-5738-90d5-9e854adc67dd'
    filters = ['hello.txt']
    level = "1"
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
    listed = base.index_archive_path(filters=filters, processing_level=level)

    assert len(listed) == 1

@longrun
def test_pipesinst_index_empty_filters(mongodb_settings, agave):
    """Indexing with empty filters returns job.archive_path x *
    """
    # This job is generated in the database by test_109#test_job_create
    # Its archive_patterns = ['ansible.png']
    job_uuid = '10797ce0-c130-5738-90d5-9e854adc67dd'
    filters = []
    level = "1"
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
    listed = base.index_archive_path(filters=filters, processing_level=level)

    assert len(listed) == 3

@longrun
def test_pipesinst_index_no_filter(mongodb_settings, agave):
    """Indexing with no filters job.archive_path x job.archive_patterns
    """
    # This job is generated in the database by test_109#test_job_create
    # Its archive_patterns = ['ansible.png']
    job_uuid = '10797ce0-c130-5738-90d5-9e854adc67dd'
    level = "1"
    base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)
    listed = base.index_archive_path(processing_level=level)
    assert len(listed) == 1

# def test_pipejob_event_fail(client_w_param):
#     """Check that fail() can happen now
#     """
#     resp = client_w_param.fail(data={'this_data': 'is from the "finish" event'})
#     assert resp['state'] == 'FAILED'

# def test_pipeinstance_re_init(mongodb_settings, agave):
#     """Verify that we can instantiate an instance of a known job without a bunch of boilerplate"""
#     job_uuid = '1071269f-b251-5a5f-bec1-6d7f77131f3f'
#     base = ManagedPipelineJobInstance(mongodb_settings, job_uuid, agave=agave)

#     assert base.archive_path.startswith('/products/v2/102')
#     assert len(base.derived_from) >= 0
#     assert len(base.child_of) > 0
#     assert len(base.pipeline_uuid) is not None

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


