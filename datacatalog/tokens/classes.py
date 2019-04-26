class Token(str):
    """An update token"""
    def __new__(cls, value, scope='user'):
        value = str(value).lower()
        setattr(cls, 'scope', scope)
        return str.__new__(cls, value)

class Salt(str):
    """A cryptographic salt"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)
