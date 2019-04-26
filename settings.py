import os
import sys
from attrdict import AttrDict
from tacconfig import config

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'localhost')

HERE = os.getcwd()
SELF = __file__
THIS = os.path.dirname(SELF)
PARENT = os.path.dirname(THIS)
GPARENT = os.path.dirname(PARENT)

# Use local not installed install of datacatalog
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from datacatalog.identifiers import abaco
from datacatalog import dicthelpers

project_settings = config.read_config(places_list=[PARENT])
bootstrap_settings = config.read_config(places_list=[THIS])
settings = dicthelpers.data_merge(project_settings, bootstrap_settings)

settings = AttrDict({
    'mongodb': settings.get(ENVIRONMENT, {}).get('mongodb'),
    'pipelines': {'pipeline_uuid': '106c46ff-8186-5756-a934-071f4497b58d',
                  'pipeline_manager_id': abaco.actorid.mock(),
                  'pipeline_manager_nonce': abaco.nonceid.mock(),
                  'job_manager_id': abaco.actorid.mock(),
                  'job_manager_nonce': abaco.nonceid.mock(),
                  'job_indexer_id': abaco.actorid.mock(),
                  'job_indexer_nonce': abaco.nonceid.mock()}

})
