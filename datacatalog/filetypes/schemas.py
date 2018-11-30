from ..jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection
from .listing import listall, listall_labels

class FileTypeLabelDoc(JSONSchemaBaseObject):
    """Schema document enumerating all FileTypeLabels"""
    pass

def get_schemas():
    """Returns the filetype_label subschema

    Returns:
        JSONSchemaCollection: One or more schema documents
    """
    labels = listall_labels()
    setup_args = {'_filename': 'filetype_label',
                  'title': 'File Type Label',
                  'type': 'string',
                  'enum': labels}
    schema = FileTypeLabelDoc(**setup_args).to_jsonschema()
    return JSONSchemaCollection({'filetype_label': schema})
