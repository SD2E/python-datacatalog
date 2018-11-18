from os import environ

class Tenant(str):
    """TACC.cloud tenant"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)
class Project(str):
    """TACC.cloud project"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)
class Username(str):
    """TACC.cloud username"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

def current_tenant():
    """Retrieve the current TACC.cloud tenant

    Returns:
        Tenant: current tenant name
    """
    return Tenant(environ.get('TENANT_ID', 'sd2e'))

def current_project():
    """Retrieve the current TACC.cloud project

    Returns:
        Project: current project name
    """
    return Project(environ.get('PROJECT_ID', 'SD2E-Community'))

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
