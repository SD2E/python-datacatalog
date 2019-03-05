import os
from .helpers import parse_boolean

__all__ = ['DATE_FORMAT', 'DNS_DOMAIN', 'TACC_PROJECT_NAME', 'TACC_PROJECT_ID',
           'TACC_PROJECT_GROUP', 'TACC_MANAGER_ACCOUNT', 'TACC_TENANT',
           'TACC_API_SERVER', 'TACC_PRIMARY_STORAGE_SYSTEM', 'TACC_JUPYTER_SERVER']

DATE_FORMAT = os.environ.get("DATE_FORMAT", "YYYYMMDDTHHmmssZZ")
DNS_DOMAIN = os.environ.get('DNS_DOMAIN', 'sd2e.org')

# TACC.cloud TAS
TACC_PROJECT_NAME = os.environ.get('TACC_PROJECT_NAME', 'SD2E-Community')
TACC_PROJECT_ID = os.environ.get('TACC_PROJECT_ID', '37391')
TACC_PROJECT_GROUP = os.environ.get('TACC_PROJECT_GROUP', '819382')

# TACC.cloud Agave/Abaco/Jupyter
TACC_TENANT = os.environ.get('TACC_TENANT', 'sd2e')
TACC_MANAGER_ACCOUNT = os.environ.get('TACC_MANAGER_ACCOUNT', 'sd2eadm')
TACC_API_SERVER = os.environ.get(
    'TACC_API_SERVER', 'https://api.' + DNS_DOMAIN + '/')
TACC_JUPYTER_SERVER = os.environ.get(
    'TACC_JUPYTER_SERVER', 'https://jupyter.' + DNS_DOMAIN)

TACC_PRIMARY_STORAGE_SYSTEM = os.environ.get(
    'TACC_PRIMARY_STORAGE_SYSTEM', 'data-sd2e-community')
