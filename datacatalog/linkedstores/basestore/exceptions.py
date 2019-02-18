from ...agavehelpers import AgaveError, AgaveHelperError

__all__ = ['CatalogError', 'CatalogQueryError', 'CatalogUpdateFailure',
           'CatalogDataError', 'CatalogDatabaseError', 'AgaveError',
           'AgaveHelperError']
class CatalogError(Exception):
    """Generic DataCatalog error has been encountered

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    pass

class CatalogQueryError(CatalogError):
    """Querying the DataCatalog has failed

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    pass

class CatalogUpdateFailure(CatalogError):
    """Writing to the DataCatalog has failed

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    pass


class CatalogDataError(CatalogError):
    """Invalid data has been encountered

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    pass


class CatalogDatabaseError(CatalogError):
    """An error has occurred that is definitely database-related

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    # Errors reading to or writing from backing store
    pass
