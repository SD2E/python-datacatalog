from ..basestore import HeritableDocumentSchema
from ..basestore import msec_precision

class JobDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=True, **kwargs):
        super(JobDocument, self).__init__(inheritance, **kwargs)
        self.update_id()

class HistoryEventDocument(HeritableDocumentSchema):
    def __init__(self, inheritance=True, document='pipelinejob_event.json',
                 filters='pipelinejob_event_filters.json', **kwargs):
        super(HistoryEventDocument, self).__init__(
            inheritance, document, filters, **kwargs)
        # create and assign Typed_UUID5
        # print('FILENAME: {}'.format(self._filename))
        udict = dict()
        for k in self.get_uuid_fields():
            udict[k] = getattr(self, k, '')
        event_uuid = self.get_typeduuid(udict, binary=False)
        setattr(self, 'uuid', event_uuid)
        filters = getattr(self, '_filters')
        # HACK. File 'filter.json' is not inherited
        filters['object']['properties'].remove('uuid')
        setattr(self, '_filters', filters)
        self.update_id()
