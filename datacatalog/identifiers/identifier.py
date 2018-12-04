
__all__ = ['IdentifierFactory', 'Identifier', 'InvalidIdentifierValue',
           'InvalidIdentifierType']

class InvalidIdentifierValue(ValueError):
    pass

class InvalidIdentifierType(TypeError):
    pass

class Identifier(str):
    """Human-readable string identifier"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class IdentifierFactory(object):

    def generate(self):
        return Identifier("identifier")

    def mock(self):
        return self.generate()

    def validate(self, value, permissive=True):

        if self.do_validate(value) is True:
            return True
        else:
            if permissive is False:
                raise ValueError(
                    '{} is not a valid identifier'.format(value))
            else:
                return False

    def do_validate(self, value, permissive=True):
        if isinstance(value, str):
            return True
        else:
            if permissive:
                return False
            else:
                raise InvalidIdentifierType("Identifier must be a string")
