__all__ = ['TenantURL', 'TenantName', 'ProjectName', 'Username']

class TenantURL(str):
    """TACC.cloud tenant base URL"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class TenantName(str):
    """TACC.cloud tenant name"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class ProjectName(str):
    """TACC.cloud project name"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class Username(str):
    """TACC.cloud username"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)
