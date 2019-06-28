import pytest
from datacatalog.tenancy import Projects, Tenants

def test_tenants():
    tenants = Tenants.sync()
    assert len(tenants.names()) > 1
    assert len(tenants.tenant_ids()) > 1
    assert not tenants.validate_tenant_id("foo", permissive=True)
    assert tenants.validate_tenant_id("sd2e", permissive=False)
    with pytest.raises(ValueError):
        tenants.validate_tenant_id("foo", permissive=False)

def test_projects():
    projects = Projects.sync()
    assert len(projects.names()) > 1
    assert len(projects.project_names()) > 1
    assert not projects.validate_project_id("foo", permissive=True)
    assert projects.validate_project_id("DARPA-BIOCON", permissive=False)
    with pytest.raises(ValueError):
        projects.validate_project_id("foo", permissive=False)