from ..basestore import CatalogError, DuplicateKeyError

class PipelineCreateFailure(CatalogError):
    pass

class DuplicatePipelineError(CatalogError):
    pass

class PipelineUpdateFailure(CatalogError):
    pass
