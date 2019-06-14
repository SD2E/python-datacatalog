from datacatalog.tenancy import Tenants, Projects
from ..jsonschemas import JSONSchemaBaseObject, JSONSchemaCollection

class TenantIdSchema(JSONSchemaBaseObject):
    """Schema document enumerating all TenantIds"""
    pass

class ProjectNameSchema(JSONSchemaBaseObject):
    """Schema document enumerating all ProjectNames"""
    pass

def get_schemas():
    """Returns the filetype_label subschema

    Returns:
        JSONSchemaCollection: One or more schema documents
    """
    return JSONSchemaCollection(
        {'tapis_tenant_id': get_tenant_id_schema(),
         'tapis_project_name': get_project_name_schema()})

def get_tenant_id_schema():
    tenant_ids = Tenants.sync().tenant_ids()
    setup_args = {'_filename': 'tapis_tenant_id',
                  'title': 'Tapis Tenant Identifier',
                  'type': 'string',
                  'enum': tenant_ids}
    return TenantIdSchema(**setup_args).to_jsonschema()

def get_project_name_schema():
    project_names = Projects.sync().project_names()
    setup_args = {'_filename': 'tapis_project_name',
                  'title': 'Tapis Project Name',
                  'type': 'string',
                  'enum': project_names}
    return ProjectNameSchema(**setup_args).to_jsonschema()
