import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    """Enables encoding of Python datetime as JSON strings"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
