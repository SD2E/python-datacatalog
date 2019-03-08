import os
from ...linkedstores.file import FileRecord, infer_filetype
from ..common import Manager, data_merge
from .indexrequest import ArchiveIndexRequest, ProductIndexRequest, get_index_request
from .indexrequest import IndexingError, IndexType, InvalidIndexingRequest
from .indexrequest import ARCHIVE, PRODUCT

class Indexer(Manager):

    def sync_listing(self, force=False):
        """Updates the job's cache of archive_path contents
        """
        if force or len(getattr(self, '_path_listing', [])) <= 0:
            listing = self.stores['pipelinejob'].list_job_archive_path(self.uuid, recurse=True, directories=False)
            setattr(self, '_path_listing', listing)
        return self

    def file_or_ref_uuid(self, string_reference):
        """Resolves a string as a file or reference UUID
        """
        uuidt = self.get_uuidtype(string_reference)
        if uuidt in ('file', 'reference'):
            return string_reference
        else:
            raise ValueError('Not a file or reference UUID')

    def file_or_ref_identifier(self, string_reference):
        """Resolves a string identifier into a files or reference UUID
        """
        doc = self.get_by_identifier(string_reference, permissive=False)
        uuidt = self.get_uuidtype(doc['uuid'])
        if uuidt in ('file', 'reference'):
            return doc['uuid']
        else:
            raise ValueError('Not a file or reference identifier')

    def file_job_relative_path(self, string_reference, check_exists=True):
        """Resolves a filename relative to a job's archive path as a file UUID
        """
        if not string_reference.startswith('./'):
            raise ValueError('Job output-relative filenames must begin with ./')
        abs_filename = os.path.normpath(
            os.path.join(self.archive_path, string_reference))
        fname_uuid = self.stores['file'].get_typeduuid(abs_filename, binary=False)
        if check_exists:
            if not self.stores['pipelinejob']._helper.exists(abs_filename, self.archive_system):
                raise ValueError('Path does not exist: {}'.format(abs_filename))
            # Ensure there's a minimal metadata record for this file entry
            # The child_of linkage is _assumed_ to be the currently job
            self.stores['file'].index(abs_filename, child_of=[self.uuid])
        return fname_uuid

    def resolve_derived_references(self, reference_set, permissive=False):
        """Resolves a list of linkages to UUIDs
        """
        resolved = list()
        for ref in reference_set:
            # UUID
            try:
                refuuid = self.file_or_ref_uuid(ref)
                resolved.append(refuuid)
                continue
            except ValueError:
                pass
                # print('Not a UUID')
            # Identifier
            try:
                refuuid = self.file_or_ref_identifier(ref)
                resolved.append(refuuid)
                continue
            except ValueError:
                pass
                # print('Not an identifier')
            # Relative path
            try:
                refuuid = self.file_job_relative_path(ref, check_exists=True)
                resolved.append(refuuid)
                continue
            except ValueError:
                pass
                # print('Not a relative filename')

            if not permissive:
                raise ValueError('Reference {} was not resolved'.format(ref))
        # list of resolved references
        return resolved

    def single_index_request(self, index_request, token=None,
                             refresh=False, fixity=True):
        """Processes a single indexing request
        """
        self.sync_listing(refresh)
        idxr = get_index_request(**index_request)
        print('idxr', idxr)
        resp = list()
        if idxr.kind is ARCHIVE:
            gen_by = idxr.get('generated_by', [])
            # Enforce presence of current job.uuid in ARCHIVE requests
            if self.uuid not in gen_by:
                gen_by.append(self.uuid)
                idxr['generated_by'] = gen_by
            resp = self._handle_single_archive_request(idxr,
                                                       token=token,
                                                       fixity=fixity)
        elif idxr.kind is PRODUCT:
            resp = self._handle_single_product_request(idxr,
                                                       token=token,
                                                       fixity=fixity)
        return resp

    def _handle_single_product_request(self, request, token=None,
                                       fixity=False, permissive=False):
        """Private: Services a products indexing request
        """
        indexed = list()
        try:
            if request.filters != []:
                patts = request.regex()
            else:
                patts = None
            for file_name in self._path_listing:
                if patts is not None:
                    if not patts.search(os.path.basename(file_name)):
                        continue
                # Create a files record
                ftype = infer_filetype(file_name,
                                       check_exists=False,
                                       permissive=True).label
                fdict = {
                    'name': file_name,
                    'type': ftype}
                frec = FileRecord(fdict)
                resp = self.stores['file'].add_update_document(frec)
                # Fixity is cheap - do it unless told not to
                if fixity:
                    try:
                        resp = self.stores['fixity'].index(file_name)
                    except Exception:
                        # It's not the end of the world if fixity indexing fails
                        print('Fixity indexing failed on {} for job {}'.format(
                            file_name, self.uuid))

                if resp is not None:
                    # print('Adding product linkages')
                    # Resolve UUIDs, indentifiers, and finally relative paths
                    # into UUIDs that can be used for linkages
                    derived_using = self.resolve_derived_references(request.derived_using, permissive=True)
                    # print('derived_using', derived_using)
                    self.stores['file'].add_link(
                        resp['uuid'], derived_using, 'derived_using')
                    derived_from = self.resolve_derived_references(request.derived_from, permissive=True)
                    # print('derived_from', derived_from)
                    self.stores['file'].add_link(
                        resp['uuid'], derived_from, 'derived_from')
                indexed.append(file_name)
            return indexed
        except Exception as mexc:
            if permissive:
                return indexed
            else:
                raise IndexingError(mexc)

    def _handle_single_archive_request(self, request, token=None,
                                       fixity=True, permissive=False):
        """Private: Services an archive path indexing request
        """
        indexed = list()
        try:
            if request.filters != []:
                patts = request.regex()
            else:
                patts = None
            for file_name in self._path_listing:
                if patts is not None:
                    if not patts.search(os.path.basename(file_name)):
                        continue
                # Create a files record
                ftype = infer_filetype(file_name,
                                       check_exists=False,
                                       permissive=True).label
                fdict = {
                    'name': file_name,
                    'type': ftype}
                if request.level is not None:
                    fdict['level'] = request.level
                frec = FileRecord(fdict)
                resp = self.stores['file'].add_update_document(frec)
                # Fixity is cheap - do it unless told not to
                if fixity:
                    try:
                        resp = self.stores['fixity'].index(file_name)
                    except Exception:
                        # It's not the end of the world if fixity indexing fails
                        print('Fixity indexing failed on {} for job {}'.format(
                            file_name, self.uuid))
                # Currently, do not honor generated_by passed the request
                if resp is not None:
                    self.stores['file'].add_link(
                        resp['uuid'], request.generated_by)
                indexed.append(file_name)
            return indexed
        except Exception as mexc:
            if permissive:
                return indexed
            else:
                raise IndexingError(mexc)
