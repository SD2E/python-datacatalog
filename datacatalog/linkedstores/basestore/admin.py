from ... import tenancy

def admin_template():
    template = {'owner': tenancy.current_username(),
                'project': tenancy.current_project(),
                'tenant': tenancy.current_tenant()}
    return template
