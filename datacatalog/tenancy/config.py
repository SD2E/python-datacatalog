from os import environ

def current_tenant():
    """Retrieve the current TACC.cloud tenant"""
    return environ.get('TENANT_ID', 'sd2e')

def current_project():
    """Retrieve the current TACC.cloud project"""
    return environ.get('PROJECT_ID', 'SD2E-Community')

def current_username():
    """Retrieve the current TACC.cloud username"""
    username_vars = ('TACC_USERNAME', 'AGAVE_USERNAME', 'JUPYTERHUB_USER')
    username = 'sd2eadm'
    for uname in username_vars:
        if environ.get(uname, None) is not None:
            username = environ.get(uname)
            break
    return username
