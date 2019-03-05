
class Level(str):
    """Representation of a data processing level"""
    MEMBERS = [('0', 'Level 0 data'),
               ('1', 'Level 1 data'),
               ('2', 'Level 2 data'),
               ('3', 'Level 3 data'),
               ('Reference', 'Reference data'),
               ('User', 'Managed user data')]

    def __new__(cls, value):
        value = str(value).title()
        if value not in dict(cls.MEMBERS):
            raise ValueError('"{}" is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)
