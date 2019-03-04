
class Linkage(str):
    """A linkage type"""
    MEMBERS = [('child_of', 'B is immutably connected to A'),
               ('generated_by', 'B was created by process or behavior of A'),
               ('derived_from', 'A was an input in creating B; B materially contains contents of A'),
               ('derived_using', 'A was needed to create B, but B does not contain its contents'),
               ('acted_on', 'B acted on A'),
               ('acted_using', 'B acted using A')]

    def __new__(cls, value):
        value = str(value).lower()
        if value not in dict(cls.MEMBERS):
            raise ValueError('"{}" is not a valid {}'.format(value, cls.__name__))
        return str.__new__(cls, value)
