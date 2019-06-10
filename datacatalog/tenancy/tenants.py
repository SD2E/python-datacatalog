import os
import json
import re
from attrdict import AttrDict

HERE = os.path.abspath(__file__)
PARENT = os.path.dirname(HERE)

class Tenant(AttrDict):
    pass

class Tenants(object):

    @classmethod
    def sync(cls):
        """Fetch the current set of Tapis tenants
        """
        # TODO - enable retrieval from tenants endpoint
        tenants_obj = Tenants()
        tenants_file = os.path.join(PARENT, 'tenants.json')
        tenants = json.load(open(tenants_file, 'r'))
        for t in tenants:
            tenant_id = t.get('code', None)
            tenant = Tenant(
                {'id': tenant_id,
                    'base_url': t.get('baseUrl', None),
                    'name': t.get('name', None),
                    'contact_email': t.get('contact', [])[0].get('email', None)}
            )
            setattr(tenants_obj, cls._propertize_tenant_id(tenant_id), tenant)
        return tenants_obj

    @classmethod
    def _propertize_tenant_id(cls, tenant_id):
        tenant_id = tenant_id.upper()
        tenant_id = tenant_id.replace('.', '_')
        if re.match('^[0-9]', tenant_id):
            tenant_id = '_' + tenant_id
        return tenant_id

    def names(self):
        """Return the property-named list of tenants
        """
        names = list()
        for prop in dir(self):
            p = getattr(self, prop)
            if isinstance(p, Tenant):
                names.append(prop)
        names.sort()
        return names

    def tenant_ids(self):
        """Return a sorted list of tenant identifiers
        """
        ids = list()
        for prop in dir(self):
            p = getattr(self, prop)
            if isinstance(p, Tenant):
                ids.append(p.id)
        ids.sort()
        return ids

    def validate_tenant_id(self, tenant_id, permissive=True):
        """Validate the supplied string against known tenant identifiers
        """
        if tenant_id in self.tenant_ids():
            return True
        else:
            if permissive is True:
                return False
            else:
                raise ValueError('{} not a known tenant id'.format(tenant_id))
