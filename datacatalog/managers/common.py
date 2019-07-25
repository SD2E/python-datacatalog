import copy
import json
import importlib
import inspect
import itertools
import re
import os
import sys
from pprint import pprint
from datacatalog.logger import get_logger
from datacatalog.hashable import picklecache, jsoncache
from datacatalog.mongo import db_connection
from datacatalog.identifiers import tacc
from functools import lru_cache
from ..linkedstores import DEFAULT_LINK_FIELDS
from ..linkages import Linkage
from .. import linkedstores
from .. import jsonschemas
from ..utils import dynamic_import
from ..tenancy import current_tenant_uri, current_username
from ..dicthelpers import data_merge
from ..agavehelpers import from_agave_uri
from ..identifiers import typeduuid
from ..extensible import ExtensibleAttrDict
from agavepy.agave import AgaveError

__all__ = ['ManagerBase', 'Manager', 'ManagerError']

class ManagerError(linkedstores.basestore.CatalogError):
    """Error has occurred inside a Manager"""
    pass

class ManagerBase(object):
    """Base class for non database, non Agave functions
    """
    def __init__(self, *args, **kwargs):
        self.logger = get_logger(__name__)

    @classmethod
    def sanitize(cls, mongo_document):
        """Strips out non-public fields from a JSON document
        """
        a = ExtensibleAttrDict(mongo_document)
        return a.as_dict(private_prefix='_')

    @classmethod
    def get_uuidtype(cls, uuid):
        """Identify the named type for a given UUID

        Args:
            uuid (str): UUID to classify by type

        Returns:
            str: Named type of the UUID
        """
        typeduuid.validate(uuid)
        return typeduuid.get_uuidtype(uuid)

    @classmethod
    def listify_uuid(cls, uuid):
        """Cast a string UUID into a list of UUIDs
        """
        if uuid is None:
            raise ValueError('"uuid" cannot be None')
        uuids = None
        if isinstance(uuid, str):
            uuids = [uuid]
        elif isinstance(uuid, list):
            uuids = uuid
        # TODO - Enforce all are catalog UUIDs
        return uuids

class Manager(ManagerBase):
    """Manages operations across LinkedStores"""
    RESOLVE_ORDER = ('file', 'reference', 'pipelinejob', 'pipeline',
                     'sample', 'measurement', 'experiment',
                     'experiment_design', 'challenge_problem', 'process',
                     'fixity', 'association',
                     'tag_annotation', 'text_annotation')
    RESOLVE_RE = re.compile('^(' + '|'.join(list(RESOLVE_ORDER)) + ').')

    def __init__(self, mongodb, agave=None, *args, **kwargs):
        ManagerBase.__init__(self, *args, **kwargs)
        # Assemble dict of stores keyed by classname
        self.api_server = kwargs.get('api_server', current_tenant_uri())
        self.mongo_client = db_connection(mongodb)
        self.client = agave
        # assert agave is not None, 'Manager requires a valid API client'
        self.stores = Manager.init_stores(self.mongo_client, agave=agave)

    @classmethod
    def init_stores(cls, mongodb, agave=None):
        # Assemble dict of stores keyed):
        stores = dict()
        for pkg in tuple(jsonschemas.schemas.STORE_SCHEMAS):
            try:
                m = dynamic_import('.' + pkg, package='datacatalog')
                store = m.StoreInterface(mongodb, agave=agave)
                store_name = getattr(store, 'schema_name')
                store_basename = store_name.split('.')[-1]
                if store_basename != 'basestore':
                    stores[store_basename] = store
            except ModuleNotFoundError:
                cls.logger.exception('Module not found: {}'.format(pkg))
        return stores

    def get_by_uuid(self, uuid, permissive=True):
        """Returns a LinkedStore document by UUID

        Args:
            uuid (str): UUID of the document to retrieve

        Returns:
            dict: The document that was retrieved
        """
        storename = self.get_uuidtype(uuid)
        resp = self.stores[storename].find_one_by_uuid(uuid)
        if resp is not None:
            return self.sanitize(resp)
        elif permissive:
            return None
        else:
            raise ValueError('That UUID does not appear to exist')

    def get_by_identifier(self, identifier_string, permissive=True):
        """Search LinkedStores for a string identifier

        Args:
            identifier_string (str): An identifier string
        Returns:
            dict: The document that was retrieved
        """

        # Is the identifer a typed UUID - no need to resolve if so
        if typeduuid.validate(identifier_string, permissive=True):
            return self.get_by_uuid(identifier_string, permissive=permissive)

        # Is the identifier a namespaced identifier (sample.tacc.xyz123)
        # If so, trust the namespace since the worst possible outcome is
        # just an empty response
        searches = self.RESOLVE_ORDER
        namespaced = self.RESOLVE_RE.search(identifier_string)
        if namespaced:
            sname = namespaced.group().replace('.', '')
            searches = [sname]

        # Finally, in order of probability (established by RESOLVE_ORDER)
        # iteratively look up identifier in each store until the string is
        # resolved or the query fails
        for sname in searches:
            store = self.stores[sname]
            for i in store.get_identifiers():
                query = {i: identifier_string}
                resp = store.coll.find_one(query)
                if resp is not None:
                    return self.sanitize(resp)
        if permissive:
            return None
        else:
            raise ValueError('No such identifier could be found')

    def get_by_uuids(self, uuids, permissive=True):
        """Returns a list of LinkedStore documents by UUID

        Args:
            uuids (list): List of document UUIDs

        Returns:
            list The document that was retrieved
        """
        recs = list()
        for uuid in uuids:
            resp = self.get_by_uuid(uuid, permissive=permissive)
            if resp is not None:
                recs.append(resp)
        sorted_recs = sorted(recs, key=lambda k: k['uuid'])
        return sorted_recs

    @picklecache.mcache(lru_cache(maxsize=256))
    def get_uuid_from_identifier(self, identifier):
        """Resolve an identifier into its corresponding UUID

        Args:
            identifier (str): A known distinct identifier from any colllection

        Returns:
            uuid: The string UUID for ``identifier``
            uuid_type: The TypedUUID type for ``uuid``
        """
        uuid = None
        uuid_type = None
        self.logger.debug('resolving {} into a UUID'.format(identifier))
        try:
            uuid_type = self.get_uuidtype(identifier)
            uuid = identifier
        except ValueError:
            resp = self.get_by_identifier(identifier)
            if resp is None:
                raise ValueError(
                    'Failed to resolve {} to a UUID'.format(identifier))
            uuid = resp.get('uuid')
            uuid_type = self.get_uuidtype(uuid)
        except Exception as exc:
            raise ValueError(
                'Failed to resolve {} to a UUID: {}'.format(identifier, exc))
        self.logger.debug(
            'identifier is a {} with UUID {}'.format(uuid_type, uuid))
        return uuid, uuid_type

    def current_tapis_user(self, permissive=False):
        """Learns the current TACC username
        """
        user = None
        try:
            user = self.client.token.username
        except AttributeError:
            user = current_username()
        except Exception:
            raise
        finally:
            return user

    @picklecache.mcache(lru_cache(maxsize=256))
    def get_tapis_user(self, username=None, permissive=False):
        """Retrieve a username record from the Tapis profile service
        """

        if username is None:
            try:
                uname = self.current_tapis_user()
                return uname
            except Exception:
                raise ValueError('Username must be resolvable from environment or provided')
        # Agave/APIM specialty accounts
        if username in tacc.username.ROLE_USERNAMES:
            return {'first_name': None, 'last_name': None, 'full_name': None,
                    'email': None, 'phone': None, 'mobile_phone': None,
                    'nonce': None, 'status': None,
                    'create_time': '20140515180317Z', 'uid': None,
                    'username': username}
        try:
            if self.client is None:
                raise AgaveError('TACC API client not initialized before use')
            else:
                return self.client.profiles.listByUsername(username=username)
        except Exception:
            if permissive:
                return None
            else:
                raise

    @picklecache.mcache(lru_cache(maxsize=256))
    def validate_tapis_username(self, username=None, permissive=False):
        """Verify the provided username against the Tapis profile service
        """
        self.get_tapis_user(username, permissive=permissive)
        return True

    @picklecache.mcache(lru_cache(maxsize=256))
    def validate_uuid(self, uuid, permissive=False):
        """Verify that a UUID5 exists in the system by retrieving it
        """
        self.get_by_uuid(uuid, permissive=permissive)
        return True

    def link(self, identifier, linked_identifier, linkage_name='child_of', token=None):
        """User-friendly method to link two Data Catalog documents

        Args:
            identifier (str): Identifier string for record to be modified
            linked_identifier (str): Identifier string for record to be linked
            linkage_name (str): A valid linkage name
            token: String token authorizing edits to target record

        Raises:
            ValueError: Raised when invalid or unknown identifers are encountered

        Returns:
            dict: The modified record, including its new linkage
        """
        self.logger.debug('linking {} -[ {} ]-> {}'.format(identifier, linkage_name, linked_identifier))
        uuid, uuid_type = self.get_uuid_from_identifier(identifier)
        linkage_name = Linkage(linkage_name)
        if isinstance(linked_identifier, str):
            linked_identifier = [linked_identifier]
        linked_uuid_values = list()
        for lindent in linked_identifier:
            luuid, luuid_type = self.get_uuid_from_identifier(lindent)
            linked_uuid_values.append(luuid)
        self.logger.debug('writing to the database')
        resp = self.stores[uuid_type].add_link(
            uuid, linked_uuid_values, relation=linkage_name, token=token)
        if resp:
            self.logger.debug('write was successful')
        return resp

    def unlink(self, identifier, linked_identifier, linkage_name='child_of', token=None):
        pass

    def get_links_from_identifier(self, identifier, linkage_name='child_of'):
        """User-friendly method to get UUIDs linked to an identifier

        Args:
            identifier (str): Identifier string for record to be modified
            linkage_name (str): A valid Linkage

        Raises:
            ValueError: Invalid or unknown identifers are encountered
            ManagerError: Failed to fetch and return linkages

        Returns:
            list: A list of TypedUUIDs for the requested linkage
        """
        self.logger.debug('getting {} links for {}'.format(linkage_name, identifier))
        uuid, uuid_type = self.get_uuid_from_identifier(identifier)
        linkage_name = Linkage(linkage_name)
        record = self.stores[uuid_type].find_one_by_uuid(uuid)
        if linkage_name in record:
            fetched_links = record.get(linkage_name, list())
            self.logger.debug('found {} links'.format(len(fetched_links)))
            fetched_links.sort()
            return fetched_links
        else:
            raise ManagerError('record type {} does not support {} linkages'.format(
                uuid_type, linkage_name))

    def derivation_from_inputs(self, inputs=[]):
        """Retrieve derived_from linkages for a set of inputs

        Args:
            inputs (list): Identifier values for one or more inputs (e.g. ``name``, ``file_id``, ``uri``)

        Returns:
            list: a set of Typed UUIDs
        """
        return self.linkage_from_inputs(inputs=inputs, target='derived_from')

    def generator_from_inputs(self, inputs=[]):
        """Retrieve generated_by linkages for a set of inputs

        Args:
            inputs (list): Identifier values for one or more inputs (e.g. ``name``, ``file_id``, ``uri``)

        Returns:
            list: a set of Typed UUIDs
        """
        return self.linkage_from_inputs(inputs=inputs, target='generated_by')

    def parent_from_inputs(self, inputs=[]):
        """Retrieve child_of linkages for a set of inputs

        Args:
            inputs (list): Identifier values for one or more inputs (e.g. ``name``, ``file_id``, ``uri``)

        Returns:
            list: a set of Typed UUIDs
        """
        return self.linkage_from_inputs(inputs=inputs, target='child_of')

    def self_from_inputs(self, inputs=[]):
        """Retrieve canonical linkage UUIDs for a list of inputs

        Args:
            inputs (list): Identifier values for one or more inputs (e.g. ``name``, ``file_id``, ``uri``)

        Returns:
            list: a set of Typed UUIDs
        """
        return self.linkage_from_inputs(inputs=inputs, target='self')

    def linkage_from_inputs(self, inputs=[], target='child_of'):
        """Retrieve linkage targets from a set of inputs

        Filepaths will be resolved against the ``file``
        collection and will return a reference to their immediate
        parent. URIs will be resolved against the ``reference`` collection
        and will return a reference to themselves.

        Args:
            inputs (list): Identifier values for one or more inputs (e.g. ``name``, ``file_id``, ``uri``)
            target (str): Linkage type to retrieve

        Returns:
            list: a set of Typed UUIDs
        """
        # STORES = [('file', 'name', 'child_of')]
        STORES = [('reference', ['uri', 'reference_id'], target),
                  ('file', ['name', 'file_id'], target)]

        if target not in DEFAULT_LINK_FIELDS and target != 'self':
            raise ValueError(
                "{} is an invalid value for 'target'. Valid options include: {}".format(target, DEFAULT_LINK_FIELDS))

        links = list()
        for idstr in inputs:
            found = False
            for store_name, search_keys, linkage in STORES:
                # print('STORE ' + store_name)
                if not isinstance(idstr, str):
                    raise ValueError(
                        "{} is a {} not a string".format(idstr, type(idstr)))
                for key in search_keys:
                    # Resolve agave URL into file.name
                    # print('KEY ' + key)
                    if store_name == 'file' and key == 'name' and idstr.startswith('agave:'):
                        agsys, agpath, agfile = from_agave_uri(idstr)
                        idstr = os.path.join(agpath, agfile)
                    query = {key: idstr}
                    resp = self.stores[store_name].find_one_by_id(**query)
                    if resp is not None:
                        if linkage == 'self':
                            # print('SELF ' + resp.get('uuid'))
                            links.extend([resp.get('uuid')])
                            found = True
                        else:
                            links.extend(resp.get(linkage, []))
                        break
                if found:
                    break
            # Break if we find the reference form for a file. Otherwise,
            # try to resolve the file record
            # if found:
            #     break
        # Filter out anything that may have come back that's not a UUID
        # Set permissive to True to simply filter out values that dont validate
        uuid_links = [l for l in links if typeduuid.validate(
            l, permissive=True) is True]
        uuid_links = list(set(uuid_links))
        uuid_links.sort()
        return uuid_links

    def lineage_from_uuid(self, query_uuid, target='child_of', permissive=True):
        """Get self-inclusive lineage for a given UUID

        Args:
            query_uuid (str): The UUID to query on
            target (str, optional): The kind of linkage to follow
            permissive (bool, optional): Whether to raise a ValueError if a
            simple lineage can't be determined.

        Raises:
            ValueError: Raised if ``permissive==False`` and complete lineage traversal cannot be achieved

        Returns:
            list: Ordered list of tuples (``<collection_level>``, ``<uuid5>``)

        Note:
            The lineage will include a reference to the original query
            at position 0. Access the UUID of immediate parent as follows:
            ``my_lineage[1][1]``.
        """

        DEFAULT_LINK_HIERARCHY = ['file', 'measurement', 'sample',
                                  'experiment', 'experiment_design',
                                  'challenge_problem']
        LINK_HIERARCHY = copy.copy(DEFAULT_LINK_HIERARCHY)
        lineage = list()

        uuid_type = typeduuid.get_uuidtype(query_uuid)
        # print('TypedUUID', uuid_type)

        for link_level in DEFAULT_LINK_HIERARCHY:
            if link_level != uuid_type:
                LINK_HIERARCHY.pop()
            else:
                break

        current_query_uuid = query_uuid
        lineage.append((uuid_type, current_query_uuid))

        try:
            for x in range(0, len(LINK_HIERARCHY)):
                try:
                    store_name = LINK_HIERARCHY[x]
                    parent_store_name = LINK_HIERARCHY[x + 1]
                    resp1 = self.stores[store_name].find_one_by_uuid(current_query_uuid)
                    if resp1 is not None:
                        parent_uuid_list = resp1.get(target, [])
                        if len(parent_uuid_list) == 1:
                            current_query_uuid = parent_uuid_list[0]
                            # lineage[parent_store_name] = current_query_uuid
                            lineage.append((parent_store_name, current_query_uuid))
                        else:
                            raise ValueError(
                                'Stopped computing lineage because {} has {} parents.'.format(
                                    current_query_uuid, len(parent_uuid_list)))
                except IndexError:
                    break
        except ValueError as verr:
            if permissive:
                print(verr)
            else:
                raise

        return lineage

    def level_from_lineage(self, lineage, level='experiment', permissive=False):
        """Traverse a lineage and return value for a specific level"""
        for name, value in lineage:
            if name == level:
                return value
        if permissive:
            return None
        else:
            raise ValueError('Failed to retrieve level {} from lineage'.format(level))

    def self_from_ids(self, ids, enforce_type=True, permissive=False):
        """Resolve UUIDs from one or more identifiers

        Args:
            ids (str/list): String or list of string identifiers
            enforce_type (bool, optional): Whether all identifiers must be of same type
            permissive (bool, optional): Whether to return None or raise exception when encountering an error

        Raises:
            ValueError: Raised when identifiers can't be resolved or type enforcement fails

        Returns:
            list: One or UUID strings
        """
        try:
            selfs = list()
            self_types = list()
            if not isinstance(ids, list):
                qids = [ids]
            else:
                qids = ids

            for qid in qids:
                quuid = None
                quuid_type = None
                try:
                    quuid_type = typeduuid.get_uuidtype(qid)
                    quuid = qid
                except Exception:
                    resp = self.get_by_identifier(qid)
                    if resp is not None:
                        quuid = resp['uuid']
                        quuid_type = typeduuid.get_uuidtype(quuid)
                if quuid is not None:
                    selfs.append(quuid)
                if quuid_type is not None:
                    self_types.append(quuid_type)

            if enforce_type:
                if len(list(set(self_types))) > 1:
                    raise ValueError('Cannot resolve a list of identifiers with mixed types')
            selfs = list(set(selfs))
            selfs.sort()
            if len(selfs) > 0:
                return selfs
            else:
                raise ValueError('Unable to resolve any identifers to UUIDs')
        except Exception:
            if permissive is True:
                return None
            else:
                raise

    def kids_from_parents(self, ids, parent='experiment',
                          parent_id='experiment_id', kid='sample',
                          kid_id='uuid', permissive=False):

        if not isinstance(ids, list):
            qids = [ids]
        else:
            qids = ids

        query_ids = list()
        child_ids = list()

        parent_coll = parent
        parent_id_field = parent_id
        child_coll = kid
        child_id_field = kid_id

        # Resolve ids into UUIDs. If ids are not valid UUIDs, consult collection
        for qid in qids:
            try:
                if typeduuid.get_uuidtype(qid) == parent:
                    query_ids.append(qid)
                else:
                    raise ValueError
            except ValueError:
                # Not a resolvable UUID with correct type
                pquery = {parent_id_field: qid}
                resp = self.stores[parent_coll].find_one_by_id(**pquery)
                if resp is not None:
                    quid = resp.get('uuid', None)
                    if quid is not None:
                        query_ids.append(quid)
        # Filter redundant members
        query_ids = list(set(query_ids))

        # Implementing N_from_N is just a lookup of N -> UUID5s
        if parent == kid:
            return query_ids

        # Get child collection records whose child_of contains query_ids
        chquery = dict()
        chquery["child_of"] = {
            "$in": query_ids
        }
        chprojection = dict()
        chprojection['uuid'] = 1.0
        chresp = self.stores[child_coll].query(chquery, projection=chprojection)
        for chrec in chresp:
            child_ids.append(chrec.get(child_id_field, None))

        # Return non-redundant set of child UUIDs
        child_ids = list(set(child_ids))
        child_ids.sort()
        return child_ids

    def designs_from_challenges(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='challenge_problem',
            parent_id='id',
            kid='experiment_design',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def experiments_from_designs(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='experiment_design',
            parent_id='experiment_design_id',
            kid='experiment',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def samples_from_experiments(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='experiment',
            parent_id='experiment_id',
            kid='sample',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def measurements_from_measurements(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='measurement',
            parent_id='measurement_id',
            kid='measurement',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def files_from_measurements(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='measurement',
            parent_id='measurement_id',
            kid='file',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def samples_from_samples(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='sample',
            parent_id='sample_id',
            kid='sample',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def experiments_from_experiments(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='experiment',
            parent_id='experiment_id',
            kid='experiment',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def measurements_from_samples(self, ids, permissive=True):
        response = self.kids_from_parents(
            ids,
            parent='sample',
            parent_id='sample_id',
            kid='measurement',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def measurements_from_experiments(self, ids, permissive=True):
        samples = self.samples_from_experiments(
            ids, permissive=permissive)
        measurements = self.measurements_from_samples(
            samples, permissive=permissive)
        measurements.sort()
        return measurements

    def measurements_from_designs(self, ids, permissive=True):
        experiments = self.experiments_from_designs(
            ids, permissive=permissive)
        return self.measurements_from_experiments(experiments, permissive=True)

    def measurements_from_challenges(self, ids, permissive=True):
        designs = self.designs_from_challenges(
            ids, permissive=permissive)
        return self.measurements_from_designs(designs, permissive=True)

    def files_from_samples(self, ids, permissive=True):
        measurements = self.measurements_from_samples(ids, permissive=True)
        response = self.kids_from_parents(
            measurements,
            parent='measurement',
            parent_id='measurement_id',
            kid='file',
            kid_id='uuid',
            permissive=permissive)
        response.sort()
        return response

    def files_from_experiments(self, ids, permissive=True):
        samples = self.samples_from_experiments(ids, permissive=True)
        response = self.files_from_samples(samples, permissive=True)
        response.sort()
        return response

    def files_from_designs(self, ids, permissive=True):
        experiments = self.experiments_from_designs(ids, permissive=True)
        response = self.files_from_experiments(experiments, permissive=True)
        response.sort()
        return response

    def jobs_from_any(self, ids, permissive=True):
        job_list = list()
        for coll in ('experiment', 'sample', 'measurement'):
            temp_list = self.kids_from_parents(ids, parent=coll,
                                               parent_id=coll + '_id',
                                               kid='pipelinejob',
                                               kid_id='uuid',
                                               permissive=True)
            job_list.extend(temp_list)
        job_list = list(set(job_list))
        job_list.sort()
        return job_list
