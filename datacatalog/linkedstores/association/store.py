from datacatalog.linkedstores.basestore import LinkedStore, SoftDelete
from datacatalog import linkages
from .document import AssociationSchema

class AssociationStore(SoftDelete, LinkedStore):
    """Manage association records"""
    LINK_FIELDS = [linkages.CONNECTS_FROM, linkages.CONNECTS_TO]

    def __init__(self, mongodb, config={}, session=None, **kwargs):
        super(AssociationStore, self).__init__(mongodb, config, session)
        schema = AssociationSchema(**kwargs)
        super(AssociationStore, self).update_attrs(schema)
        self.setup(update_indexes=kwargs.get('update_indexes', False))

class StoreInterface(AssociationStore):
    pass
