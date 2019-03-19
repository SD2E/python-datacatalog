import collections
from datacatalog.extensible import ExtensibleAttrDict

class Record(ExtensibleAttrDict):
    """New document for BaseStore with schema enforcement"""

    PARAMS = [
        ('uuid', False, 'uuid', None),
        ('child_of', False, 'child_of', []),
        ('generated_by', False, 'generated_by', []),
        ('derived_using', False, 'derived_using', []),
        ('derived_from', False, 'derived_from', [])]

    def __init__(self, value, *args, **kwargs):

        # Ensure the minimum set of other fields is populated
        ovalue = value
        # We use a bespoke process rather than relying on the schema for now
        # because file record creation cannot tolerate the overhead of
        # materializing a class definition with python_jsonschema_objects
        for param, req, attr, default in self.PARAMS:
            val = kwargs.get(param, ovalue.get(param, default))
            if val is not None:
                value[param] = val

        super().__init__(value)
