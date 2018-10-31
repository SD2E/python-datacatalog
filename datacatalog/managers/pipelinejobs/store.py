
from .. import identifiers
from ..jobs import PipelineJobStore

class PipelineJob(PipelineJobStore):
    PARAMS = [('lab_name', True, 'lab_name', None),
              ('experiment_reference', True, 'experiment_reference', None),
              ('sample_id', True, 'sample_id', None),
              ('measurement_id', False, 'measurement_id', None),
              ('data', False, 'data', {})]

    def __init__(self, reactor, **kwargs):
        for param, mandatory, attr, default in self.PARAMS:
            try:
                value = (kwargs[param] if mandatory
                         else kwargs.get(param, default))
            except KeyError:
                raise KeyError(
                    'parameter "{}" is mandatory'.format(param))
            setattr(self, attr, value)

        super(PipelineJob, self).__init__(reactor.settings.pipelines,
                                          reactor.settings.get('catalogstore', {}),
                                          session=reactor.nickname)

        self.actor_id = getattr(reactor, 'uid')
        self.execution_id = getattr(reactor, 'execid')

        # Configure to talk to manager actor
        settings = getattr(reactor, 'settings')
        self.pipeline_uuid = settings['pipelines'].get('pipeline_uuid')
        self.__manager = settings['pipelines'].get('job_manager_id')
        self.__nonce = settings['pipelines'].get('updates_nonce')
