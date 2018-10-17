from jsonschemas import JSONSchemaBaseObject
from .typed_uuid import UUIDType

class CatalogUUID(JSONSchemaBaseObject):
    def __init__(self, **kwargs):
        super(CatalogUUID, self).__init__(**kwargs)
        self.title = 'Catalog UUID'
        self.description = 'UUID5 with DNS namespacing'
        # self.format = 'uri'
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
        self.pattern = '^(uri:urn:)?' + kwargs.get('prefix', '100') + '[0-9a-f]{5}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        super(TypedCatalogUUID, self).update_id()

def get_schemas():
    schemas = dict()
    for key, uuidt in UUIDType.items():
        setup_args = {'_filename': key.title(),
                      'title': uuidt.title + ' UUID',
                      'prefix': uuidt.prefix}
        schemas[key + '_uuid'] = TypedCatalogUUID(**setup_args).to_jsonschema()
    return schemas
