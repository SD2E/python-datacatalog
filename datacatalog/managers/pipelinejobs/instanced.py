
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
        self._add_event_functions()

    def _add_event_functions(self):

        ename = None
        for ename, esec in EVENT_DEFS:
            def fn(data={}, token=None):
                event_doc = {
                    'uuid': self.uuid,
                    'token': getattr(self, 'token', token),
                    'name': ename,
                    'data': data}
                return self.handle(
                    event_doc, token=token)
            setattr(self, ename, fn)

    def handle(self, event_doc, token=None):
        """Override super().handle to process events directly rather than by name
        """
        return self.stores['pipelinejob'].handle(event_doc, token)

    def index(self, level="1", filters=None, fixity=True, token=None):
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
                                           fixity=fixity)

    def indexed(self, token=None):
        """Mark job outputs indexing as completed
        """
        event_doc = {'uuid': self.uuid, 'name': 'indexed'}
        resp = self.handle(event_doc, token=token)
        return resp

    def index_archive_path(self, processing_level="1", filters=None, fixity=True, note=None):
        """Discover files in a job archive path and associate with the job``````````````````

        Args:
            processing_level (str, optional): "Processing level" for the new file records
            filters (list, optional): Python regular expressions to subselect specific files in target path. Overrides job.archive_patterns.
            fixity (bool, optional): Whether to update a fixity record for the file as well

        Note:
            Regular expressions are concatenated into a single expression at
            run time. This may impact construction of your filter strings. For
            example, ``['sample.tacc.1', 'sample-tacc-1']`` will be evaluated
            as Python regex ``sample.tacc.1|sample-tacc-1``.

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
        if not isinstance(filters, list):
            archive_patterns = getattr(self, 'archive_patterns', [])
            for ap in archive_patterns:
                index_req = None
                if isinstance(ap, dict):
                    index_req = IndexRequest(**ap)
                elif isinstance(ap, str):
                    index_req = IndexRequest(processing_level='1', filters='ap', fixity=True, note='Translated from legacy string representation')
                if index_req is not None:
                    index_iterations.append(index_req)
        elif filters != []:
            # Build a new index request from kwargs
            index_req = IndexRequest(
                processing_level=processing_level, filters=filters,
                fixity=fixity, note=note)
            index_iterations.append(index_req)

        # No sense doing an expensive files listing if there aren't any
        # indexing requests. Eject, eject, eject!
        if len(index_iterations) > 0:
            return indexed

        # Do the path listing only once
        path_listing = self.stores['pipelinejob'].list_job_archive_path(
            self.uuid, recurse=True, directories=False)

        fixity_iterations = list()
        for idxr in index_iterations:
            if idxr.fixity is True:
                fixity_iterations.append(idxr)
            self.build_metadata_index(idxr, path_listing)

            for file in path_listing:
                # If patterns is not specified
                if patts is not None:
                    if not patts.search(os.path.basename(file)):
                        continue

                # Create a 'files' metadata record and associate with job UUID
                #
                # Note: We're only currently guaranteed to resolve the filetype
                # by its name. The full POSIX path is required to use content
                # signature or Linux magic and I am not sure we have that in
                # 'file' at this point in the code
                ftype = getattr(infer_filetype(
                    file, check_exists=False, permissive=True), 'label')
                frec = FileRecord(
                    {'name': file, 'type': ftype, 'level': processing_level})
                resp = FileRecord(
                    self.stores['file'].add_update_document(frec))
                # Add the job UUID to any file's existing
                gen_by = resp.get('generated_by', list())
                if self.uuid not in gen_by:
                    gen_by.append(self.uuid)
                    resp['generated_by'] = gen_by
                    resp = self.stores['file'].add_update_document(resp)

                # Create a 'fixities' record
                #
                # Technically, this is an add-update operation but as these are
                # output files they are not likely to have been indexed before
                #
                # Fixity is not critical - it can easily be picked up
                # later if we miss it for some reason. It's just cheap &
                # convenient to try and do it here. Hence, it's a configurable
                # option and it only lohs a warning instead of excepting on failure
                if fixity:
                    try:
                        self.stores['fixity'].index({'name': file})
                    except Exception as exc:
                        logger.warning(
                            'Failed to capture fixity for {}: {}'.format(file, exc))

                # Add the file's basename to a list of indexed files
                # which we will return
                # TODO - assess whether to return the original path instead
                indexed.append((os.path.basename(file), resp['uuid'], resp['type']))

                # Throw in an elapsed check so we can learn how long indexing,
                # an expensive operation, takes.
                # TODO - is there a centralized performance logging tool for Python
                elapsed_time = microseconds() - start_time
                logger.info('INDEXED {} in {} usec'.format(
                    resp['uuid'], elapsed_time))

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
            patts = index_request.regex()
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
                resp = FileRecord(
                    self.stores['file'].add_update_document(frec))
                # Link the new file record to its generating job
                if resp is not None:
                    self.stores['file'].add_link(
                        resp['uuid'], self.uuid, 'generated_by')
                    indexed.append(file_name)
            return indexed
        except Exception as mexc:
            if permissive:
                return indexed
            else:
                raise IndexingError(mexc)


    def build_fixity_index(self, files, index_request):
        pass
