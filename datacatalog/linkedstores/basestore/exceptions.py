
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *

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
