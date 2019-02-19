from __future__ import print_function
import os
from .helpers import parse_boolean

__all__ = ['DATE_FORMAT', 'DNS_DOMAIN', 'TACC_PROJECT_NAME', 'TACC_PROJECT_ID',
           'TACC_PROJECT_GROUP', 'TACC_MANAGER_ACCOUNT', 'TACC_TENANT',
           'TACC_API_SERVER', 'TACC_PRIMARY_STORAGE_SYSTEM']

DATE_FORMAT = os.environ.get("CATALOG_DATE_FORMAT", "YYYY-MM-DD")

DNS_DOMAIN = os.environ.get('CATALOG_DNS_DOMAIN', 'sd2e.org')

# TACC.cloud TAS
TACC_PROJECT_NAME = os.environ.get('CATALOG_TACC_PROJECT_NAME', 'SD2E-Community')
TACC_PROJECT_ID = os.environ.get('CATALOG_TACC_PROJECT_ID', '37391')
TACC_PROJECT_GROUP = os.environ.get('CATALOG_TACC_PROJECT_GROUP', '819382')

# TACC.cloud Agave/Abaco/Jupyter
TACC_TENANT = os.environ.get('CATALOG_TACC_TENANT', 'sd2e')
TACC_MANAGER_ACCOUNT = os.environ.get('CATALOG_TACC_MANAGER_ACCOUNT', 'sd2eadm')
TACC_API_SERVER = os.environ.get(
    'CATALOG_TACC_API_SERVER', 'https://api.' + DNS_DOMAIN + '/')

TACC_PRIMARY_STORAGE_SYSTEM = os.environ.get(
    'CATALOG_TACC_PRIMARY_STORAGE_SYSTEM', 'data-sd2e-community')

# settings = {
#     "auth_password_login_enabled": PASSWORD_LOGIN_ENABLED,
#     "auth_saml_enabled": SAML_LOGIN_ENABLED,
#     "auth_saml_entity_id": SAML_ENTITY_ID,
#     "auth_saml_metadata_url": SAML_METADATA_URL,
#     "auth_saml_nameid_format": SAML_NAMEID_FORMAT,
#     "date_format": DATE_FORMAT,
#     "auth_jwt_login_enabled": JWT_LOGIN_ENABLED,
#     "auth_jwt_auth_issuer": JWT_AUTH_ISSUER,
#     "auth_jwt_auth_public_certs_url": JWT_AUTH_PUBLIC_CERTS_URL,
#     "auth_jwt_auth_audience": JWT_AUTH_AUDIENCE,
#     "auth_jwt_auth_algorithms": JWT_AUTH_ALGORITHMS,
#     "auth_jwt_auth_cookie_name": JWT_AUTH_COOKIE_NAME,
#     "auth_jwt_auth_header_name": JWT_AUTH_HEADER_NAME,
#     "feature_show_permissions_control": FEATURE_SHOW_PERMISSIONS_CONTROL,
# }
