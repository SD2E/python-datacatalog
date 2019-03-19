
import arrow
import os
import re
import sys
import validators
import logging
from pprint import pprint
from datacatalog import settings

from ... import identifiers
from ...utils import microseconds
from ..common import Manager, data_merge
from ...tokens import get_token
from ...linkedstores.basestore import DEFAULT_LINK_FIELDS as LINK_FIELDS
from ...linkedstores.basestore import formatChecker
from ...linkedstores.annotation import InlineAnnotationDocument
from ...linkedstores.file import FileRecord, infer_filetype
from ...linkedstores.pipelinejob.fsm import EVENT_DEFS

from ...identifiers.typeduuid import catalog_uuid, uuid_to_hashid, get_uuidtype
from .config import PipelineJobsConfig, DEFAULT_ARCHIVE_SYSTEM
from .exceptions import ManagedPipelineJobError
from .indexer import Indexer, IndexingError, InvalidIndexingRequest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ManagedPipelineJobInstance(Indexer):
    """Supports working with a existing ManagedPipelineJob

    Args:
        mongodb (mongo.Connection): Connection to MongoDB with write access to ``jobs``
        uuid (str): Job UUID
        token (str): Update token for the job
    """
    # Bring in only minimal set of fields to lift from parent document as
    # the intent of this class is not to update the ManagedPipelineJob but
    # only to take actions that depend on its specific properties
    PARAMS = [
        ('state', False, 'state', None),
        ('archive_path', False, 'archive_path', None),
        ('archive_system', False, 'archive_system', DEFAULT_ARCHIVE_SYSTEM),
        ('archive_patterns', False, 'archive_patterns', []),
        ('product_patterns', False, 'product_patterns', []),
        ('generated_by', False, 'generated_by', []),
        ('child_of', False, 'child_of', []),
        ('acted_on', False, 'acted_on', []),
        ('acted_using', False, 'acted_using', []),
        ('pipeline_uuid', False, 'pipeline_uuid', None)]

    def __init__(self, mongodb, uuid, agave=None, **kwargs):
        super(ManagedPipelineJobInstance, self).__init__(mongodb, agave)
        self.uuid = uuid
        db_rec = self.stores['pipelinejob'].find_one_by_uuid(uuid)
        for param, req, attr, default in self.PARAMS:
            setattr(self, attr, db_rec.get(param))
        # Dynamically add run, fail, etc methods
        # self._add_event_functions()

    # def _add_event_functions(self):

    #     ename = None
    #     for ename, esec in EVENT_DEFS:
    #         def fn(data={}, token=None):
    #             event_doc = {
    #                 'uuid': self.uuid,
    #                 'token': getattr(self, 'token', token),
    #                 'name': ename,
    #                 'data': data}
    #             return self.handle(
    #                 event_doc, token=token)
    #         setattr(self, ename, fn)

    def handle(self, event_doc, token=None):
        """Override super().handle to process events directly rather than by name
        """
        return self.stores['pipelinejob'].handle(event_doc, token)

    def index(self, token=None, transition=False, level='1',
              fixity=False, filters=None, **kwargs):
        """Index the contents of the job's archive path
        """
        # if filters are passed, parse thru them and assign to either archive
        # or product index queue then dispatch. If not, pull results from
        # <kind>_patterns files and do same.

        # Iterate through filters if provided
        filter_set = list()
        if filters is not None and isinstance(filters, list):
            self.logger.debug('custom index() request')
            if len(filters) >= settings.MAX_INDEX_FILTERS:
                # For now, log a warning but if this becomes a recurring
                # problem, we will raise an Exception
                self.logger.warning(
                    'index() with {} or more filters is not supported'.format(
                        settings.MAX_INDEX_FILTERS))
            filter_set = filters
            index_fixity = fixity
        else:
            # We index the defaults if no filters are provided
            for patt_key in ('archive_patterns', 'product_patterns'):
                f = getattr(self, patt_key, list())
                if isinstance(f, list) and len(f) > 0:
                    filter_set.extend(f)
            index_fixity = True

        # Process the event
        indexed = list()
        try:
            self.sync_listing(force=True)
            event_doc = {'uuid': self.uuid,
                         'name': 'index',
                         'data': {}}
            resp = self.handle(event_doc, token=token)
            if resp is None:
                raise IndexingError('Empty event response')
        except Exception:
            self.logger.exception('Failed to process event')
            raise

        # Do the metadata indexing
        for index_request_str in filter_set:
            self.logger.debug('handling request {}'.format(index_request_str))
            try:
                just_indexed = self.single_index_request(
                    index_request_str, token=token,
                    refresh=False, fixity=index_fixity)
                indexed.extend(just_indexed)
            except IndexingError:
                self.logger.exception(
                    'Indexing attempt failed: {}'.format(index_request_str))
                raise

        self.logger.info('Indexed {} job files'.format(len(indexed)))

        if transition is True:
            self.logger.info("Sending 'indexed' to {}".format(self.uuid))
            return self.indexed(token=token)
        else:
            return list(set(indexed))

    def indexed(self, token=None):
        """Mark job outputs indexing as completed
        """
        event_doc = {'uuid': self.uuid, 'name': 'indexed'}
        resp = self.handle(event_doc, token=token)
        return resp
