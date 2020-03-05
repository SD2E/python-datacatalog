import base64
import json
from copy import copy
from jsondiff import diff
from pprint import pprint
from ...settings import MONGO_DELETE_FIELD
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

def diff_list(list1, list2):
    list1_set = set()
    list2_set = set()
    list_diff = []
    # O(3N) time
    # index list 2
    for index, element in enumerate(list2):
        list2_set.add(str(index) + str(element))

    # check list1 against list2, index list1
    for index, element in enumerate(list1):
        list1_set.add(str(index) + str(element))
        check = str(index) + str(element)
        if check not in list2_set:
            list_diff.append(str(element))

    # check list 2 against list1
    for index, element in enumerate(list2):
        check = str(index) + str(element)
        if check not in list1_set:
            list_diff.append(str(element))

    return list_diff

# https://github.com/xlwings/jsondiff/issues/18
# Lists are evaluated recursively and lead to maximum recursion depth exceeded in comparisons
# A potential work-around: scan through the two documents, diffing "long" lists as we go,
# remove them from the JSON document, perform the regular jsondiff comparison,
# and merge the diffs back into the result
# "long" lists here are lists with over 100 elements
def diff_remove_long_lists(doc1, doc2):
    CANDIDATE_LIST_LENGTH = 100

    # return results here
    diff_dict = {}

    # long lists we will check
    candidate_long_list_keys = set()

    # track lists of objects and dictionaries as separate candidates; recurse
    candidate_dict_keys = set()
    candidate_list_keys = set()

    for candidate_key in doc1:
        candidate = doc1[candidate_key]
        if isinstance(candidate, list):
            if len(candidate) > CANDIDATE_LIST_LENGTH:
                candidate_long_list_keys.add(candidate_key)
            else:
                candidate_list_keys.add(candidate_key)
        elif isinstance(candidate, dict):
            candidate_dict_keys.add(candidate_key)
    for candidate_key in doc2:
        candidate = doc2[candidate_key]
        if isinstance(candidate, list):
            if len(candidate) > CANDIDATE_LIST_LENGTH:
                candidate_long_list_keys.add(candidate_key)
            else:
                candidate_list_keys.add(candidate_key)
        elif isinstance(candidate, dict):
            candidate_dict_keys.add(candidate_key)

    # diff the long list
    for candidate_long_list_key in candidate_long_list_keys:
        if candidate_long_list_key in doc1 and candidate_long_list_key in doc2:
            list1 = doc1[candidate_long_list_key]
            list2 = doc2[candidate_long_list_key]
            list_diff = diff_list(list1, list2)
            del doc1[candidate_long_list_key]
            del doc2[candidate_long_list_key]
            if len(list_diff) > 0:
                diff_dict[candidate_long_list_key] = list_diff

    # recurse on child dictionary keys
    for candidate_dict_key in candidate_dict_keys:
        if candidate_dict_key in doc1 and candidate_dict_key in doc2:
            child1 = doc1[candidate_dict_key]
            child2 = doc2[candidate_dict_key]

            (child1, child2, child_diff_dict) = diff_remove_long_lists(child1, child2)

            # update children in case they are modified
            doc1[candidate_dict_key] = child1
            doc2[candidate_dict_key] = child2

            # merge into parent result
            if len(child_diff_dict) > 0:
                diff_dict[candidate_dict_key] = child_diff_dict

    # recurse on child list keys
    for candidate_list_key in candidate_list_keys:
        if candidate_list_key in doc1 and candidate_list_key in doc2:
            child1_array = doc1[candidate_list_key]
            child2_array = doc2[candidate_list_key]

            # type check - make sure these are both lists
            if not isinstance(child1_array, list) :
                diff_dict[candidate_list_key] = child1_array
                continue
            if not isinstance(child2_array, list):
                diff_dict[candidate_list_key] = child2_array
                continue

            for index, child1 in enumerate(child1_array):
                if index < len(child2_array):
                    child2 = child2_array[index]
                    # are these objects? primitives would be caught above
                    if type(child1) == dict and type(child2) == dict:
                        (child1, child2, child_diff_dict) = diff_remove_long_lists(child1, child2)

                        # update list children in case they are modified
                        child1_array[index] = child1
                        child2_array[index] = child2

                        # merge parent result
                        # track using an index key
                        if len(child_diff_dict) > 0:
                            diff_dict[candidate_list_key + "_" + str(index)] = child_diff_dict

            # update child lists in case they are modified
            doc1[candidate_list_key] = child1_array
            doc2[candidate_list_key] = child2_array

    return (doc1, doc2, diff_dict)


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
        # Filter _private keys save for the system-wide soft-delete field
        for key in list(doc.keys()):
            if key.startswith('_') and key != MONGO_DELETE_FIELD:
                del doc[key]
        safe_docs.append(json.loads(json.dumps(doc, cls=DateTimeEncoder)))

    # doc1 and doc2 have have their long lists removed, diffs are in diff_dict
    (doc1, doc2, diff_dict) = diff_remove_long_lists(safe_docs[0], safe_docs[1])

    delta = diff(doc1, doc2, syntax='explicit', dump=True)

    # delta is a string - inline any long list diffs if they exist
    if len(diff_dict) > 0:
        delta_json = json.loads(delta)
        delta_json.update(diff_dict)
        delta = json.dumps(delta_json)

    doc_diff_obj = DocumentDiff(delta, doc_uuid, doc_admin, action)
    return doc_diff_obj
