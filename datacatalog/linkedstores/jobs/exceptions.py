from ..basestore import CatalogError, DuplicateKeyError

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
