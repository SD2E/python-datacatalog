from attrdict import AttrDict

class ExtensibleAttrDict(dict):
    """Implements AttrDict-like behavior for complex objects"""

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

    def as_dict(self, filters=[], private_prefix='__'):
        d = dict(self)
        # Filter privates
        if private_prefix is not None:
            for k in list(d.keys()):
                if k.startswith(private_prefix):
                    try:
                        d.pop(k)
                    except KeyError:
                        pass
        # Filter filters
        for f in filters:
            try:
                d.pop(f)
            except KeyError:
                pass
        return d
