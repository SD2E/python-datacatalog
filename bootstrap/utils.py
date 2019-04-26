import json

def to_json_abstract(python_obj, length=64):
    return json.dumps(python_obj, separators=(',', ':'))[0:(length - 1)]
