import json

# replace periods with | for all json/dictionary keys
# cleaning prior to mongo ingest for IP parameters
def clean_keys(parameter_item):
    new_keys = {}
    del_keys = []
    for key in parameter_item:
        del_keys.append(key)
        new_key = key
        if "." in new_key:
            new_key = new_key.replace(".", "|")
        new_keys[new_key] = parameter_item[key]
    for del_key in del_keys:
        del parameter_item[del_key]
    for new_key in new_keys:
        new_item = new_keys[new_key]
        if isinstance(new_item, dict):
            clean_keys(new_item)
        parameter_item[new_key] = new_item

def to_json_abstract(python_obj, length=64):
    return json.dumps(python_obj, separators=(',', ':'))[0:(length - 1)]
