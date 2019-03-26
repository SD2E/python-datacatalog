DEFAULT_MANAGED_FIELDS = ('uuid', '_admin', '_properties',
                          '_salt', '_enforce_auth')

UUID = 'uuid'
ADMIN = '_admin'
PROPERTIES = '_properties'
SALT = '_salt'
AUTH = '_enforce_auth'

DEFINITIONS = {UUID: 'Typed, managed UUID5 identifier',
               ADMIN: 'Tenancy and user information',
               PROPERTIES: 'Revision information',
               SALT: 'Pseudorandom string used to generate the record-specific token',
               AUTH: 'Enforce token authentication'}

ALL = (UUID, ADMIN, PROPERTIES, SALT, AUTH)
PRIVATE = (ADMIN, PROPERTIES, SALT, AUTH)

class ManagedFieldError(ValueError):
    pass

class ManagedField(str):
    """A MongoDB managed field"""
    def __new__(cls, value):
        value = str(value).lower()
        setattr(cls, 'description', DEFINITIONS.get(value))
        if value not in list(DEFINITIONS.keys()):
            raise ManagedFieldError('"{}" is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)
