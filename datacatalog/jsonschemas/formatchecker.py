import jsonschema

class formatChecker(jsonschema.FormatChecker):
    """Enables python-jsonschema to validate ``format`` fields"""

    def __init__(self):
        jsonschema.FormatChecker.__init__(self)
