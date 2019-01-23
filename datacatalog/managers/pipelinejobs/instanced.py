
import arrow
import os
import re
import sys
import validators
import logging
from pprint import pprint
from ... import identifiers
from ..common import Manager, data_merge
from ...tokens import get_token
from ...linkedstores.basestore import DEFAULT_LINK_FIELDS as LINK_FIELDS
from ...linkedstores.basestore import formatChecker
from ...linkedstores.file import FileRecord, infer_filetype
from ...identifiers.typeduuid import catalog_uuid, uuid_to_hashid
from .config import PipelineJobsConfig, DEFAULT_ARCHIVE_SYSTEM
from .exceptions import ManagedPipelineJobError


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ManagedPipelineJobInstance(Manager):
    """Supports working with a existing ManagedPipelineJob

    Args:
        mongodb (mongo.Connection): Connection to system MongoDB with write access to ``jobs``
        uuid (str): Job UUID
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
        ('acts_on', False, 'acts_on', []),
        ('acts_using', False, 'acts_using', []),
        ('pipeline_uuid', False, 'pipeline_uuid', None)]

    def __init__(self, mongodb, uuid, agave=None, **kwargs):
        super(ManagedPipelineJobInstance, self).__init__(mongodb, agave)
        self.uuid = uuid
        db_rec = self.stores['pipelinejob'].find_one_by_uuid(uuid)
        for param, req, attr, default in self.PARAMS:
            setattr(self, attr, db_rec.get(param))

    def index_archive_path(self, processing_level="1", filters=None, fixity=True):
        """Discover files in a job archive path and associate with the job

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
        indexed = list()

        # Add values passed as 'filters' to override value for
        # job.archive_patterns
        if not isinstance(filters, list):
            filters = getattr(self, 'archive_patterns', [])
        if filters != []:
            patts = re.compile('|'.join(filters))
        else:
            patts = None

        if self.state in ('INDEXING', 'FINISHED'):
            path_listing = self.stores['pipelinejob'].list_job_archive_path(self.uuid, recurse=True, directories=False)
            for file in path_listing:

                if patts is not None:
                    if not patts.search(os.path.basename(file)):
                        continue

                # Create a files record
                #
                # When called with this signature, infer_filetype will
                # always return a FileType object
                ftype = getattr(infer_filetype(file,
                                               check_exists=False,
                                               permissive=True), 'label')
                frec = FileRecord({'name': file,
                                    'type': ftype,
                                    'level': processing_level})
                resp = FileRecord(self.stores['file'].add_update_document(frec))

                # Add this job's UUID to the file's existing
                gen_by = resp.get('generated_by', list())
                if self.uuid not in gen_by:
                    gen_by.append(self.uuid)
                    resp['generated_by'] = gen_by
                    resp = self.stores['file'].add_update_document(resp)
                indexed.append((os.path.basename(file), resp['uuid'], resp['type']))

                # Create a fixities record
                #
                if fixity:
                    try:
                        self.stores['fixity'].index({'name': file})
                    except Exception as exc:
                        logger.warning(
                            'Failed to capture fixity for {}: {}'.format(file, exc))
                # print('INDEXED {}'.format(resp['uuid']))
            return indexed
        else:
            raise ManagedPipelineJobError('Job was not in "INDEXING" or "FINISHED" state')
