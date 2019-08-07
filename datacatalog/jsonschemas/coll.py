__all__ = ['JSONSchemaCollection']

class JSONSchemaCollection(dict):
    """Collection of JSON schemas indexed by basename(schema filename)"""
    def __new__(cls, value):
        return dict.__new__(cls, value)
