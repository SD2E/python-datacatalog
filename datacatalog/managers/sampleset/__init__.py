import jsonschemas
import linkedstores
from .processor import SampleSetProcessor

CHILD_OF = [('experiment', 'challenge_problem'),
            ('sample', 'experiment'),
            ('measurement', 'sample'),
            ('file', 'measurement'),
            ('pipelinejob', 'pipeline'),
            ('file', 'pipelinejob')]
