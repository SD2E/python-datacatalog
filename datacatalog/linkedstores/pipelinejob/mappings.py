class AgaveEvents(object):
    """Maps between Agave API and Pipeline job events"""
    agavejobs = {
        'CREATED': 'resource',
        'UPDATED': 'updated',
        'DELETED': 'fail',
        'PERMISSION_GRANT': 'resource',
        'PERMISSION_REVOKE': 'resource',
        'PENDING': 'resource',
        'STAGING_INPUTS': 'resource',
        'CLEANING_UP': 'resource',
        'ARCHIVING': 'resource',
        'STAGING_JOB': 'resource',
        'FINISHED': 'finish',
        'KILLED': 'update',
        'FAILED': 'fail',
        'STOPPED': 'fail',
        'RUNNING': 'run',
        'PAUSED': 'resource',
        'QUEUED': 'resource',
        'SUBMITTING': 'resource',
        'STAGED': 'resource',
        'PROCESSING_INPUTS': 'resource',
        'ARCHIVING_FINISHED': 'resource',
        'ARCHIVING_FAILED': 'fail',
        'HEARTBEAT': 'update'
    }
