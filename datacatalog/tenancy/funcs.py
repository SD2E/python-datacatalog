from os import environ
from datacatalog import settings
from .classes import TenantURL, TenantName, ProjectName, Username

__all__ = ['current_username', 'current_tenant',
           'current_tenant_uri', 'current_project',
           'current_admin_username']

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
                     '_abaco_username',
                     'USER')
    for uname in username_vars:
        if environ.get(uname, None) is not None:
            username = environ.get(uname)
            return Username(username)
    raise ValueError('No TACC.cloud username could be found in the environment')


def current_admin_username():
    """Retrieve the TACC.cloud tenant admin username

    Returns:
        Username: tenant admin username
    """
    return Username(settings.TACC_MANAGER_ACCOUNT)
