from .processor import SampleSetProcessor, UnknownReference, SampleSetProcessorError

CHILD_OF = [('experiment_design', 'challenge_problem'),
            ('experiment', 'experiment_design'),
            ('sample', 'experiment'),
            ('measurement', 'sample'),
            ('file', 'measurement'),
            ('pipelinejob', 'pipeline'),
            ('file', 'pipelinejob')]

__all__ = ['SampleSetProcessor']
