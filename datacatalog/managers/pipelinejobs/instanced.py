
import arrow
import os
import re
import sys
import validators
import logging
from pprint import pprint
from ... import identifiers
from ...utils import microseconds
from ..common import Manager, data_merge
from ...tokens import get_token
from ...linkedstores.basestore import DEFAULT_LINK_FIELDS as LINK_FIELDS
from ...linkedstores.basestore import formatChecker
from ...linkedstores.annotation import InlineAnnotationDocument
from ...linkedstores.file import FileRecord, infer_filetype
from ...linkedstores.pipelinejob.fsm import EVENT_DEFS

from ...identifiers.typeduuid import catalog_uuid, uuid_to_hashid
from .config import PipelineJobsConfig, DEFAULT_ARCHIVE_SYSTEM
from .exceptions import ManagedPipelineJobError
from .indexing import IndexRequest, IndexingError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ManagedPipelineJobInstance(Manager):
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

    def index(self, level="1", filters=None, fixity=True,
              token=None, child_of=None, generated_by=None,
              derived_from=None, derived_using=None):
        """Index the job outputs
        """
        event_doc = {'uuid': self.uuid, 'name': 'index',
                     'data': {'level': level,
                              'filters': filters,
                              'fixity': fixity}}
        resp = self.handle(event_doc, token=token)
        if resp is not None:
            return self.index_archive_path(processing_level=level,
                                           filters=filters,
                                           fixity=fixity,
                                           child_of=child_of,
                                           generated_by=generated_by,
                                           derived_from=derived_from,
                                           derived_using=derived_using)

    def indexed(self, token=None):
        """Mark job outputs indexing as completed
        """
        event_doc = {'uuid': self.uuid, 'name': 'indexed'}
        resp = self.handle(event_doc, token=token)
        return resp

    def index_archive_path(self, processing_level="1", filters=None,
                           fixity=True, note=None,
                           child_of=None, generated_by=None,
                           derived_from=None, derived_using=None):
        """Discover files in a job archive path and associate with the job``````````````````

        Args:
            processing_level (str, optional): "Processing level" for the new file records
            filters (list, optional): Python regular expressions to subselect specific files in target path. Overrides job.archive_patterns.
            fixity (bool, optional): Whether to update a fixity record for the file as well
            child_of: (str, optional): UUID of the parent for indexed files
            derived_from: (str, optional): UUID of a file or reference from which all members of the path are derived
            derived_using: (str, optional): UUID of a file or reference used to derived all members of the path
            generated_by: (str, optional): UUID of a pipeline or process that is calling this function

        Note:
            1. If no value for ``filters`` is passed, the function will run any
            indexing patterns defined in the job's ``archive_patterns`` list.
            2. The ``filters`` regexes are concatenated into a single expression at
            run time. This may impact construction of your filter strings. For
            example, ``['sample.tacc.1', 'sample-tacc-1']`` will be evaluated
            as Python regex ``sample.tacc.1|sample-tacc-1``.
            3. Linkage parameters passed in to this function will apply to all indexed files

        Returns:
            list: Filenames set as ``generated_by`` the specified job
        """
        start_time = microseconds()
        indexed = list()

        # Assemble a list of indexing operations
        #
        # Passing a non-empty 'filters' list indicates that the specified
        # indexing action, rather than the defaults, are to be performed
        index_iterations = list()
        if isinstance(filters, list) and filters != []:
            # Build a new index request from kwargs
            index_req = IndexRequest(
                processing_level=processing_level, filters=filters,
                fixity=fixity, note=note, child_of=child_of,
                derived_from=derived_from, derived_using=derived_using,
                generated_by=generated_by)
            index_iterations.append(index_req)
        elif filters is None:
            archive_patterns = getattr(self, 'archive_patterns', [])
            print('PATTERNS', archive_patterns)
            if archive_patterns != []:
                for ap in archive_patterns:
                    index_req = None
                    if isinstance(ap, dict):
                        # print('FORMATTING', ap)
                        index_req = IndexRequest(**ap)
                    elif isinstance(ap, list):
                        # print('TRANSLATING', ap)
                        index_req = IndexRequest(
                            processing_level='1',
                            filters=ap,
                            fixity=True,
                            note='Translated from legacy list representation',
                            child_of=child_of,
                            derived_from=derived_from,
                            derived_using=derived_using,
                            generated_by=generated_by)
                    if index_req is not None:
                        print('INDEX_REQ', index_req)
                        index_iterations.append(index_req)
            else:
                print('INDEXING ALL FILES')
                index_req = IndexRequest(
                    processing_level=processing_level,
                    filters=[],
                    fixity=fixity,
                    note='Request to index all files',
                    child_of=child_of,
                    derived_from=derived_from,
                    derived_using=derived_using,
                    generated_by=generated_by)
                index_iterations.append(index_req)

        # If, somehow, there are no index requests, skip the expensive file
        # listing and return an empty list
        if len(index_iterations) == 0:
            return indexed

        # Do path listing once and re-use it for each index iteration
        path_listing = self.stores['pipelinejob'].list_job_archive_path(
            self.uuid, recurse=True, directories=False)

        fixity_iterations = list()
        for idxr in index_iterations:
            if idxr.fixity is True:
                fixity_iterations.append(idxr)
                # raise SystemError(idxr)
            result = self.build_metadata_index(path_listing, idxr)
            if isinstance(result, list):
                indexed.extend(result)

        for idxr in fixity_iterations:
            result = self.build_fixity_index(path_listing, idxr)
            if isinstance(result, list):
                indexed.extend(result)

        # Make list non-redundant
        indexed = list(set(indexed))
        elapsed_time = microseconds() - start_time
        logger.info('INDEXED {} in {} usec'.format(self.uuid, elapsed_time))
        return indexed

    def build_metadata_index(self, files_list, index_request, permissive=False):
        """Associates files matching an IndexRequest to the current job

        Args:
            files_list (list): List of absolute filepaths
            index_request (IndexRequest): The specification for matching patterns and so on
            permissive (bool, optional): Whether to raise an Exception on error

        Raises:
            IndexingError: Raised (when permssive is False) when an error occurs

        Returns:
            list: String names of successfully indexed files
        """
        indexed = list()
        try:
            # filters will always be a list
            if index_request.filters != []:
                patts = index_request.regex()
            else:
                patts = None
            print('FILES', len(files_list))
            print('PATTS', patts)
            for file_name in files_list:
                # If patterns is not specified
                if patts is not None:
                    if not patts.search(os.path.basename(file_name)):
                        continue

                # Create a 'files' record and associate with job UUID
                #
                # Note: We make an attempt to guess filetype but without
                # guaranteed access to the physical file, we're limited
                # to what can be learned from the filename.
                ftype = getattr(infer_filetype(
                    file_name, check_exists=False, permissive=True), 'label')
                frec = FileRecord(
                    {'name': file_name,
                     'type': ftype,
                     'level': index_request.processing_level})
                # Transform the note from the archving request into InlineAnnotation
                if index_request.note is not None:
                    frec['notes'] = [InlineAnnotationDocument(
                        data=index_request.note)]
                resp = self.stores['file'].add_update_document(frec)
                # Build linkages
                if resp is not None:
                    self.stores['file'].add_link(
                        resp['uuid'], self.uuid, 'generated_by')
                    # Generated by is repeated here in case the caller wants to
                    # make another linkage
                    for linkf in ['child_of', 'derived_from', 'derived_using', 'generated_by']:
                        linkattr = getattr(index_request, linkf)
                        if isinstance(linkattr, (str, list)):
                            if linkf is not None:
                                try:
                                    self.stores['file'].add_link(resp['uuid'], linkattr, linkf)
                                except Exception:
                                    print('Failed adding linkage {}-{}-{}'.format(
                                        resp['uuid'], linkf, linkattr))
                    indexed.append(file_name)
            return indexed
        except Exception as mexc:
            if permissive:
                return indexed
            else:
                raise IndexingError(mexc)

    def build_fixity_index(self, files_list, index_request, permissive=False):
        """Indexes fixity for each file in files_list matching an IndexRequest

        Args:
            files_list (list): List of absolute filepaths
            index_request (IndexRequest): The specification for matching patterns and so on
            permissive (bool, optional): Whether to raise an Exception on error

        Raises:
            IndexingError: Raised (when permssive is False) when an error occurs

        Returns:
            list: String names of successfully indexed files
        """
        indexed = list()
        try:
            # filters will always be a list
            if index_request.filters != []:
                patts = index_request.regex()
            else:
                patts = None
            for file_name in files_list:
                # If patterns is not specified
                if patts is not None:
                    if not patts.search(os.path.basename(file_name)):
                        continue
                try:
                    print('STORES.FIXITY.INDEX ' + file_name)
                    # We only pass along generated_by - Fixity is much more constrained
                    self.stores['fixity'].index(
                        file_name, generated_by=index_request.generated_by)
                    indexed.append(file_name)
                except Exception as exc:
                    logger.warning(
                        'Failed to record fixity for {}: {}'.format(
                            file_name, exc))
            return indexed
        except Exception as mexc:
            if permissive:
                return indexed
            else:
                raise IndexingError(mexc)
