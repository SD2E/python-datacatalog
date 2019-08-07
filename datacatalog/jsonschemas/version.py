__all__ = ['MAJOR_VERSION', 'MINOR_VERSION', 'PATCH', 'TAG', \
           'VERSION', 'TEXT_VERSION',
           'JSONSCHEMA_SPECIFICATION']

JSONSCHEMA_SPECIFICATION = 'draft-07'
MAJOR_VERSION = 2
MINOR_VERSION = 2
PATCH = 0
TAG = 'master'

VERSION = (MAJOR_VERSION,
           MINOR_VERSION,
           PATCH,
           TAG)

TEXT_VERSION = '{}.{}.{}#{}'.format(*list(VERSION))
