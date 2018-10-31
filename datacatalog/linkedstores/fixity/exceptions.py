from ..basestore import CatalogError, DuplicateKeyError

class FixtyUpdateFailure(CatalogError):
    pass

class FixityDuplicateError(DuplicateKeyError):
    pass

class FixtyNotFoundError(KeyError):
    pass
