import base64
import json
from copy import copy
from jsondiff import diff
from pprint import pprint
from datacatalog import linkages, settings
from datacatalog.extensible import ExtensibleAttrDict
from datacatalog.jsonschemas import DateTimeEncoder
from datacatalog.utils import time_stamp, current_time, msec_precision

CREATE = 'create'
DELETE = 'delete'
REPLACE = 'replace'
UPDATE = 'update'
ACTIONS = (CREATE, DELETE, REPLACE, UPDATE)
DEFAULT_ACTION = UPDATE

class DocumentDiff(ExtensibleAttrDict):
    def __init__(self, delta, uuid, admin, action):
        setattr(self, 'delta', delta)
        setattr(self, 'uuid', uuid)
        setattr(self, 'admin', admin)
        setattr(self, 'action', action)
        setattr(self, 'timestamp', msec_precision(current_time()))

    def __delta_dict(self):
        return json.dumps(json.loads(self.delta), sort_keys=True, 
                          indent=0, separators=(',', ':'))

    def __doc(self, encoded=True):
        delta_enc = self.__delta_dict()
        if encoded:
            delta_enc = base64.urlsafe_b64encode(delta_enc.encode('utf-8'))
        doc = {'uuid': self.uuid, 
                'date': self.timestamp, 
                'diff': delta_enc,
                'action': self.action,
                '_admin': self.admin}
        return doc

    def document(self, encoded=True):
        """Renders DiffRecord into a MongoDB-compatible record
        """
        return self.__doc(encoded)

    def json(self, encoded=True):
        return json.dumps(self.document(encoded), 
                          sort_keys=True, 
                          separators=(',', ':'), 
                          cls=DateTimeEncoder)

    def __repr__(self):
        return self.json(encoded=False)

    @property
    def updated(self):
        """Were any differences found?
        """
        return json.loads(self.delta) != dict()

def get_diff(source={}, target={}, action=DEFAULT_ACTION):
    """Determine the differences between two documents

    Generates a document for the `updates` store that describes the diff
    between source and target documents. The resulting document includes
    the document UUID, a timestamp, the document's tenancy details, and
    the JSON-diff encoded in URL-safe base64. The encoding is necessary
    because JSON diff and patch formats include keys beginning with `$`,
    which are prohibited in MongoDB documents.

    Args:
        source (dict): Source document
        target (dict): Target document
        action (str): Type of update action to represent

    Returns:
        dict: A json-diff record
        LinkEdgesDiff: a record of differences in linkage fields
        bool: Whether the json-diff was empty or not
    """

    if action not in ACTIONS:
        raise ValueError('{} is not a valid update log action'.format(action))

    doc_uuid = source.get('uuid', target.get('uuid', None))
    if doc_uuid is None:
        raise KeyError('No "uuid" in source or target')

    doc_admin = source.get('_admin', target.get('_admin', {}))
    
    cmp_source_doc = copy(source)
    cmp_target_doc = copy(target)
    docs = [cmp_source_doc, cmp_target_doc]
    safe_docs = list()
    for doc in docs:
        # strip linkages
        for lf in linkages.ALL:
            if lf in doc:
                del doc[lf]
        # strip identifiers
        for filt in ('uuid', '_id'):
            if filt in doc:
                del doc[filt]
        # _private keys
        for key in list(doc.keys()):
            if key.startswith('_'):
                del doc[key]
        safe_docs.append(json.loads(json.dumps(doc, cls=DateTimeEncoder)))

    delta = diff(safe_docs[0], safe_docs[1], syntax='explicit', dump=True)

    doc_diff_obj = DocumentDiff(delta, doc_uuid, doc_admin, action)
    return doc_diff_obj
