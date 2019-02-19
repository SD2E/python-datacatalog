from os import environ
from .. import settings

__all__ = ['current_username', 'current_tenant',
           'current_tenant_uri', 'current_project']
class TenantURL(str):
    """TACC.cloud tenant nase URL"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)
class TenantName(str):
    """TACC.cloud tenant"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)
class ProjectName(str):
    """TACC.cloud project"""
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
    return TenantURL(environ.get('TENANT_BASE)URL', 'https://api.sd2e.org'))

def current_tenant():
    """Retrieve the current TACC.cloud tenant

    Returns:
        TenantName: current tenant name
    """
    return TenantName(environ.get('TENANT_ID', 'sd2e'))

def current_project():
    """Retrieve the current TACC.cloud project

    Returns:
        ProjectName: current project name
    """
    return ProjectName(environ.get('PROJECT_ID', 'SD2E-Community'))

def current_username():
    """Retrieve the current TACC.cloud username

    Returns:
        Username: current username
    """
    username_vars = ('TACC_USERNAME', 'AGAVE_USERNAME', 'JUPYTERHUB_USER')
    username = 'sd2eadm'
    for uname in username_vars:
        if environ.get(uname, None) is not None:
            username = environ.get(uname)
            break
    return Username(username)
