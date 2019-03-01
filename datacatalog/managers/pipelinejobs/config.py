from ...extensible import ExtensibleAttrDict

DEFAULT_ARCHIVE_SYSTEM = 'data-sd2e-community'

class CorePipelinesConfig(ExtensibleAttrDict):
    def __init__(self, **kwargs):
        PARAMS = [
            ('api_server', False, 'api_server', 'https://api.sd2e.org')]
        super(CorePipelinesConfig, self).__init__()
        for param, required, attr, default in PARAMS:
            if param in kwargs:
                value = kwargs.get(param, default)
                if required and value is None:
                    raise ValueError(
                        '{} is required to initialize {}'.format(
                            param, self.__class__.__name__))
                setattr(self, attr, value)

class PipelinesConfig(CorePipelinesConfig):

    def __init__(self, **kwargs):
        PARAMS = [('pipeline_manager_id', True, 'pipeline_manager_id', None),
                  ('pipeline_manager_nonce', False, 'pipeline_manager_nonce', None)]
        super(PipelinesConfig, self).__init__(**kwargs)
        for param, required, attr, default in PARAMS:
            if param in kwargs:
                value = kwargs.get(param, default)
                if required and value is None:
                    raise ValueError(
                        '{} is required to initialize {}'.format(
                            param, self.__class__.__name__))
                setattr(self, attr, value)

class PipelineJobsConfig(CorePipelinesConfig):
    """A PipelineJobs configuration.

    Implements sanity on ``init()`` checking to avoid misconfigured Pipeline
    Jobs agents.
    """

    def __init__(self, **kwargs):
        PARAMS = [('job_manager_id', True, 'job_manager_id', None),
                  ('job_manager_nonce', False, 'job_manager_nonce', None),
                  ('job_indexer_id', True, 'job_indexer_id', None),
                  ('job_indexer_nonce', False, 'job_indexer_nonce', None),
                  ('pipeline_uuid', True, 'pipeline_uuid', None)]
        super(PipelineJobsConfig, self).__init__(**kwargs)
        for param, required, attr, default in PARAMS:
            if param in kwargs:
                value = kwargs.get(param, default)
                if required and value is None:
                    raise ValueError(
                        '{} is required to initialize {}'.format(
                            param, self.__class__.__name__))
                setattr(self, attr, value)
