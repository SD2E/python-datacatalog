from os import environ
from .. import settings

__all__ = ['current_username', 'current_tenant',
           'current_tenant_uri', 'current_project',
           'current_admin_username']
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

def current_tenant_uri():
    """Retrieve the current TACC.cloud tenant

    Returns:
        TenantURL: current tenant base URI
    """
    return TenantURL(settings.TACC_API_SERVER)

def current_tenant():
    """Retrieve the current TACC.cloud tenant

    Returns:
        TenantName: current tenant name
    """
    return TenantName(settings.TACC_TENANT)

def current_project():
    """Retrieve the current TACC.cloud project

    Returns:
        ProjectName: current project name
    """
    return ProjectName(settings.TACC_PROJECT_NAME)

def current_username():
    """Retrieve the current TACC.cloud username

    Returns:
        Username: current username

    Raises:
        ValueError: This is raised on failure to find a username
    """
    username_vars = ('TACC_USERNAME', 'AGAVE_USERNAME',
                     'JUPYTERHUB_USER',
                     '_abaco_username')
    for uname in username_vars:
        if environ.get(uname, None) is not None:
            username = environ.get(uname)
            return Username(username)
    raise ValueError('No TACC.cloud username could be found in the current environment')


def current_admin_username():
    """Retrieve the TACC.cloud tenant admin username

    Returns:
        Username: tenant admin username
    """
    return Username(settings.TACC_MANAGER_ACCOUNT)
