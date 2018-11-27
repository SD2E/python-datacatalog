from ..jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from .listing import listall, listall_labels

class FileTypeLabel(JSONSchemaBaseObject):
    pass

def get_schemas():
    """Return the filetype_label subschema

    Returns:
        dict: One or more schemas
    """
    labels = listall_labels()
    setup_args = {'_filename': 'filetype_label',
                  'title': 'File Type Label',
                  'type': 'string',
                  'enum': labels}
    schema = FileTypeLabel(**setup_args).to_jsonschema()
    return JSONSchemaCollection({'filetype_label': schema})
