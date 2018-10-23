
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object
class EventMappings(object):
    """Mapping between Agave API job status and Pipeline Jobs events"""
    agavejobs = {
        'CREATED': None,
        'UPDATED': None,
        'DELETED': None,
        'PERMISSION_GRANT': None,
        'PERMISSION_REVOKE': None,
        'PENDING': None,
        'STAGING_INPUTS': 'update',
        'CLEANING_UP': None,
        'ARCHIVING': 'update',
        'STAGING_JOB': None,
        'FINISHED': 'finish',
        'KILLED': 'update',
        'FAILED': 'fail',
        'STOPPED': 'fail',
        'RUNNING': 'run',
        'PAUSED': None,
        'QUEUED': 'update',
        'SUBMITTING': None,
        'STAGED': None,
        'PROCESSING_INPUTS': None,
        'ARCHIVING_FINISHED': 'update',
        'ARCHIVING_FAILED': 'fail',
        'HEARTBEAT': 'update'
    }
