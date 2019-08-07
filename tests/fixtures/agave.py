import pytest
import json
import os
import random
import agavepy.agave as a
import warnings
from attrdict import AttrDict
from datacatalog.identifiers import random_string

PWD = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)

__all__ = ['credentials', 'agave',
           'agave_app_id', 'agave_job_id',
           'aloe_job_id']

# Valid environment variable prefixes to parameterize tests
PREFIXES = ['TAPIS', '_TAPIS', 'AGAVE', '_AGAVE', 'TACC', '_TACC']

@pytest.fixture(scope='session')
def credentials():
    """
    Imports Agave credentials into the testing session

    Import order:
    1. Test credentials in PWD
    2. User's credential store
    3. Environment variables
    """
    credentials = {}

    # test credentials file
    try:
        credentials_file = os.environ.get('AGAVE_CREDENTIALS_FILE',
                                          'test_credentials.json')
        credentials_file_path = os.path.join(PWD, credentials_file)

        if os.path.exists(credentials_file):
            # print(("Loading from file {}".format(credentials_file)))
            credentials = json.load(open(credentials_file_path, 'r'))
            return credentials
    except Exception:
        pass
        # warnings.warn(
        #     'No credentials file found. Using contents of $AGAVE_CACHE_DIR')

    # user credential store
    try:
        cdir = os.environ.get('TAPIS_CACHE_DIR',
                              os.environ.get(
                                  'AGAVE_CACHE_DIR', None))
        if cdir is not None:
            ag_cred_store = os.path.join(
                cdir, 'current')
        else:
            ag_cred_store = os.path.expanduser('~/.agave/current')

        if os.path.exists(ag_cred_store):
            # print("Loading from credential store {}".format(ag_cred_store))
            tempcred = json.load(open(ag_cred_store, 'r'))
            # Translate from agave/current format
            credentials['apiserver'] = tempcred.get('baseurl', None)
            credentials['username'] = tempcred.get('username', None)
            credentials['password'] = tempcred.get('password', None)
            credentials['apikey'] = tempcred.get('apikey', None)
            credentials['apisecret'] = tempcred.get('apisecret', None)
            credentials['token'] = tempcred.get('access_token', None)
            credentials['refresh_token'] = tempcred.get('refresh_token', None)
            credentials['verify_certs'] = True
            credentials['client_name'] = tempcred.get('client_name', None)
            credentials['tenantid'] = tempcred.get('tenantid', None)
            return credentials
    except Exception:
        # print("Error loading user credential store: {}".format(e))
        pass

    # load from environment
    # print("Loading from environment variables")
    for env in ('apikey', 'apisecret', 'username', 'password', 'apiserver',
                'verify_certs', 'refresh_token', 'token', 'client_name',
                'tenantid', 'client_name'):
        for varname_root in PREFIXES:
            varname = varname_root + env.upper()
            if os.environ.get(varname, None) is not None:
                credentials[env] = os.environ.get(varname)
                break

    return credentials


@pytest.fixture(scope='session')
def agave(credentials):
    """Returns a functional Agave client
    """
    aga = a.Agave(
        client_name=credentials.get('client_name'),
        username=credentials.get('username'),
        password=credentials.get('password'),
        api_server=credentials.get('apiserver'),
        api_key=credentials.get('apikey'),
        api_secret=credentials.get('apisecret'),
        token=credentials.get('token'),
        refresh_token=credentials.get('refresh_token'),
        verify=True)
    return aga

@pytest.fixture(scope='session')
def agave_app_id():
    """Generates a random (but schema-compliant) Agave Apps identifier
    """
    app_name = random_string(int(random.random() * 18) + 6).lower()
    app_version = (int(random.random() * 10),
                   int(random.random() * 10),
                   int(random.random() * 10))
    return '{0}-{1}.{2}.{3}'.format(app_name, *app_version)

@pytest.fixture(scope='session')
def agave_job_id():
    """Returns an Agave Job identifier
    """
    return '6583653933928541720-242ac11b-0001-007'

@pytest.fixture(scope='session')
def aloe_job_id():
    """Returns an Aloe Job identifier
    """
    return 'd608e5d2-6a16-41b2-bbf5-fd848cbd70a3-007'
