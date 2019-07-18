from ..schemas import JSONSchemaBaseObject, JSONSchemaCollection

UUIDTYPES = [('generic', '100', 'Generic Data Catalog Record'),
             ('challenge_problem', '101', 'Challenge Problem'),
             ('experiment_design', '114', 'Experiment Design or Request'),
             ('experiment', '102', 'Experiment'),
             ('sample', '103', 'Sample'),
             ('measurement', '104', 'Measurement'),
             ('file', '105', 'File Metadata'),
             ('fixity', '116', 'File Fixity'),
             ('pipeline', '106', 'Pipeline'),
             ('pipelinejob', '107', 'PipelineJob'),
             ('pipelinejob_event', '108', 'PipelineJob Event'),
             ('process', '117', 'Named Computational Process'),
             ('reference', '109', 'Named Reference File or URI'),
             ('product', '110', 'Output from a PipelineJob'),
             ('upload', '111', 'Uploaded File'),
             ('annotation', '118', 'User-contributed Free-text Annotation'),
             ('inline_annotation', '119', 'Machine-generated Free-text Annotation'),
             ('dashboard', '121', 'Redash Dashboard'),
             ('query', '120', 'Redash Query'),
             ('input_classifier', '115', 'Input File Classifier'),
             ('tag_annotation', '122', 'Tag Annotation'),
             ('text_annotation', '123', 'Text Annotation'),
             ('association', '124', 'Annotation Association'),
             ('structured_request', '125', 'Structured Experiment Request')
             ]

class TypedUUID(object):
    """UUID identifying a catalog object and advertising its internal type"""

    def __init__(self, *args):
        self.key = args[0]
        self.prefix = args[1]
        self.title = args[2]

    def __len__(self):
        return len(self.prefix)

class CatalogUUID(JSONSchemaBaseObject):
    def __init__(self, **kwargs):
        super(CatalogUUID, self).__init__(**kwargs)
        self.title = 'Catalog'
        self.description = 'UUID5 with DNS namespacing'
        self.pattern = '^(uri:urn:)?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        self._filename = 'CatalogUUID'
        self.type = 'string'
        self.examples = []
        self.update_id()
        self._kind = 'generic'

    def update_id(self):
        schema_id = self.BASEREF + self._filename + '_uuid.json'
        schema_id = schema_id.lower()
        setattr(self, 'id', schema_id)

# class TypedCatalogUUID(CatalogUUID):
#     def __init__(self, **kwargs):
#         super(TypedCatalogUUID, self).__init__(**kwargs)
#         self._filename = kwargs.get('_filename', None)
#         self.title = kwargs.get('title', None)
#         self.description = self.title + ' ' + self.description
#         self.pattern = '^(uri:urn:)?' + kwargs.get('prefix', '100') + '[0-9a-f]{5}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
#         super(TypedCatalogUUID, self).update_id()

UUIDType = dict()
for uuidt, prefix, title in UUIDTYPES:
    UUIDType[uuidt] = TypedUUID(uuidt, prefix, title)
