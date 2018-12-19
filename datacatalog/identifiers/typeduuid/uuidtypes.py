from ..schemas import JSONSchemaBaseObject, JSONSchemaCollection

UUIDTYPES = [('generic', '100', 'Catalog Object'),
             ('challenge_problem', '101', 'Challenge Problem'),
             ('experiment', '102', 'Experiment'),
             ('sample', '103', 'Sample'),
             ('measurement', '104', 'Measurement'),
             ('file', '105', 'File'),
             ('pipeline', '106', 'Pipeline'),
             ('pipelinejob', '107', 'PipelineJob'),
             ('pipelinejob_event', '108', 'PipelineJob Event'),
             ('reference', '109', 'Reference Asset'),
             ('product', '110', 'PipelineJob Product'),
             ('upload', '111', 'Uploaded File'),
             ('dashboard', '113', 'Redash Dashboard'),
             ('experiment_design', '114', 'Experiment Design'),
             ('input_classifier', '115', 'Input File Classifier'),
             ('fixity', '116', 'File Fixity Entry')]

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
        self.title = 'Catalog UUID'
        self.description = 'UUID5 with DNS namespacing'
        self.pattern = '^(uri:urn:)?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        self._filename = 'CatalogUUID'
        self.type = 'string'
        self.update_id()

    def update_id(self):
        schema_id = self.BASEREF + self._filename + '_uuid.json'
        schema_id = schema_id.lower()
        setattr(self, 'id', schema_id)

class TypedCatalogUUID(CatalogUUID):
    def __init__(self, **kwargs):
        super(TypedCatalogUUID, self).__init__(**kwargs)
        self._filename = kwargs.get('_filename', None)
        self.title = kwargs.get('title', None)
        self.description = self.title + ' ' + self.description
        self.pattern = '^(uri:urn:)?' + kwargs.get('prefix', '100') + '[0-9a-f]{5}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        super(TypedCatalogUUID, self).update_id()

UUIDType = dict()
for uuidt, prefix, title in UUIDTYPES:
    UUIDType[uuidt] = TypedUUID(uuidt, prefix, title)
