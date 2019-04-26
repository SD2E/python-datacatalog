__all__ = ['InvalidToken', 'InvalidAdminToken']

class InvalidToken(ValueError):
    """Raised when a token is invalid"""
    pass

class InvalidAdminToken(InvalidToken):
    """Raised when an administrative token is invalid"""
    pass
