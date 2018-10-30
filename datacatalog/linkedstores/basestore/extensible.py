
class ExtensibleAttrDict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def as_dict(self, filters=[]):
        d = dict(self)
        for f in filters:
            try:
                d.pop(f)
            except KeyError:
                pass
        return d
