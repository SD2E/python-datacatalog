from ..jsonschemas import JSONSchemaBaseObject
from .listing import listall, listall_labels

def get_schemas():
    """Return the filetype_label schema

    Returns:
        dict: One or more schemas
    """
    labels = listall_labels()
    setup_args = {'_filename': 'filetype_label',
                  'title': 'File Type Label',
                  'type': 'string',
                  'enum': labels}
    schema = JSONSchemaBaseObject(**setup_args).to_jsonschema()
    return {'filetype_label': schema}
