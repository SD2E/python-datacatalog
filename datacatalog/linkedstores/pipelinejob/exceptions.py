from ..basestore import CatalogError, DuplicateKeyError

__all__ = ['JobError', 'JobCreateFailure', 'JobUpdateFailure',
           'DuplicateJobError', 'UnknownPipeline', 'UnknownJob']
class JobError(Exception):
    pass

class JobCreateFailure(JobError):
    pass

class JobUpdateFailure(JobError):
    pass

class DuplicateJobError(DuplicateKeyError):
    pass

class UnknownPipeline(JobError):
    pass

class UnknownJob(JobError):
    pass
