from ..basestore import CatalogError, DuplicateKeyError

__all__ = ['JobError', 'JobCreateFailure', 'JobUpdateFailure',
           'DuplicateJobError', 'UnknownPipeline', 'UnknownJob']

class JobError(Exception):
    """A generic job error"""
    pass

class JobCreateFailure(JobError):
    """Job was not created"""
    pass

class JobUpdateFailure(JobError):
    """Job was not updated"""
    pass

class DuplicateJobError(DuplicateKeyError):
    """Job was a duplicate which is not allowed"""
    pass

class UnknownPipeline(JobError):
    """The referenced pipeline is not known"""
    pass

class UnknownJob(JobError):
    """The referenced job is not known"""
    pass
