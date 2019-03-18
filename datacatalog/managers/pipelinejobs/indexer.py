import os
from datacatalog import settings
from ...linkedstores.file import FileRecord, infer_filetype
from ...agavehelpers import from_agave_uri, AgaveError
from ..common import Manager, data_merge
from .indexrequest import ArchiveIndexRequest, ProductIndexRequest, get_index_request
from .indexrequest import IndexingError, IndexType, InvalidIndexingRequest
from .indexrequest import ARCHIVE, PRODUCT

class Indexer(Manager):

    _path_listing = list()

    def sync_listing(self, force=False):
        """Updates the job's cache of archive_path contents
        """
        if force or len(getattr(self, '_path_listing', [])) <= 0:
            listing = self.stores['pipelinejob'].list_job_archive_path(self.uuid, recurse=True, directories=False)
            if isinstance(listing, list):
                setattr(self, '_path_listing', listing)
            else:
                raise IndexingError('Failed to list archive path')
        return self

    def index_if_exists(self, abs_filename, storage_system=None, check_exists=True):
        """Index a file if it can be confirmed to exist
        """
        if storage_system is None:
            storage_system is settings.STORAGE_SYSTEM
        elif storage_system != settings.STORAGE_SYSTEM:
            # NOTE - This is temporary until comprehensive support for storageSystems is complete
            raise ValueError(
                'Only storage system {} is currently supported'.format(
                    settings.STORAGE_SYSTEM))

        if check_exists:
            if not self.stores['pipelinejob']._helper.exists(abs_filename, storage_system):
                raise ValueError('Path does not exist: {}'.format(abs_filename))

        # TODO - Add storage_system=storage_system to File/FixityStore.index()
        self.logger.info('Indexing referenced file {}'.format(
            os.path.basename(abs_filename)))
        resp = self.stores['file'].index(abs_filename, child_of=[self.uuid])
        # raise SystemError(resp)
        try:
            self.stores['fixity'].index(abs_filename)
        except Exception:
            if settings.LOG_FIXITY_ERRORS:
                self.logger.exception('Fixity indexing failed for {}'.format(abs_filename))
        return resp

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
        if doc is not None:
            uuidt = self.get_uuidtype(doc['uuid'])
            if uuidt in ('file', 'reference'):
                return doc['uuid']
        else:
            # Try to index a file path if it wasn't in the database
            if string_reference.startswith('/'):
                doc = self.index_if_exists(string_reference)
                if doc is not None:
                    return doc['uuid']
        raise ValueError('Not a valid file or reference identifier {}'.format(string_reference))

    def file_agave_url(self, string_reference, check_exists=True):
        """Resolves an Agave URL into a file UUID
        """
        # Needs to be wrapped in try..except block since from_agave_uri
        # raises AgaveError or ValueError when it cannot resolve a URI
        try:
            system, directory, fname = from_agave_uri(string_reference)
            abs_filename = os.path.join(directory, fname)
            self.index_if_exists(abs_filename, system, check_exists=check_exists)
            return self.file_or_ref_identifier(abs_filename)
        except Exception:
            raise ValueError('Unable to resolve Agave URI')

    def file_job_relative_path(self, string_reference, check_exists=True):
        """Resolves a filename relative to a job's archive path as a file UUID
        """
        if not string_reference.startswith('./'):
            raise ValueError('Job output-relative filenames must begin with ./')
        abs_filename = os.path.normpath(
            os.path.join(self.archive_path, string_reference))
        fname_uuid = self.stores['file'].get_typeduuid(abs_filename, binary=False)
        if check_exists:
            self.index_if_exists(abs_filename, self.archive_system)
        return fname_uuid

    def resolve_derived_references(self, reference_set, permissive=False):
        """Resolves a list of linkages to UUIDs
        """
        resolved = set()
        for ref in reference_set:
            self.logger.debug('resolving {}'.format(ref))

            # UUID
            try:
                refuuid = self.file_or_ref_uuid(ref)
                resolved.add(refuuid)
                self.logger.debug('Was a UUID')
                continue
            except ValueError:
                self.logger.debug('Not a UUID')

            # Identifier
            try:
                refuuid = self.file_or_ref_identifier(ref)
                resolved.add(refuuid)
                self.logger.debug('Was a string identifier')
                continue
            except ValueError:
                self.logger.debug('Not a string identifier')

            try:
                refuuid = self.file_agave_url(ref)
                resolved.add(refuuid)
                self.logger.debug('Was an Agave files url')
                continue
            except ValueError:
                self.logger.debug('Not an Agave files url')

            # Relative path
            try:
                refuuid = self.file_job_relative_path(ref, check_exists=True)
                resolved.add(refuuid)
                self.logger.debug('Was a relative path')
                continue
            except ValueError:
                self.logger.debug('Not a relative path')

            if not permissive:
                raise ValueError('String reference {} was not resolved'.format(ref))
        # list of resolved references
        resolved_list=list(resolved)
        resolved_list.sort()
        self.logger.info('Resolved {} records'.format(len(resolved_list)))
        return resolved_list

    def single_index_request(self, index_request, token=None,
                             refresh=False, fixity=True):
        """Processes a single indexing request
        """
        self.sync_listing(refresh)
        idxr = get_index_request(**index_request)
        self.logger.debug('IndexRequest: {}'.format(idxr))
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
        indexed = set()
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
                resp = self.stores['file'].add_update_document(fdict)
                # Fixity is cheap - do it unless told not to
                if fixity:
                    try:
                        resp = self.stores['fixity'].index(file_name)
                    except Exception:
                        # It's not the end of the world if fixity indexing fails
                        self.logger.debug(
                            'Fixity indexing failed on {} for job {}'.format(
                                file_name, self.uuid))

                if resp is not None:
                    self.logger.debug('Adding product linkages')
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
                indexed.add(file_name)

            indexed_list = list(indexed)
            indexed_list.sort()
            self.logger.debug('indexed {} items'.format(len(indexed_list)))
            return indexed_list

        except Exception as mexc:
            if permissive:
                return indexed
            else:
                raise IndexingError(mexc)

    def _handle_single_archive_request(self, request, token=None,
                                       fixity=True, permissive=False):
        """Private: Services an archive path indexing request
        """
        indexed = set()
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
                fdict_kwargs = dict()
                if request.level is not None:
                    fdict['level'] = request.level
                resp = self.stores['file'].add_update_document(fdict)
                # Fixity is cheap - do it unless told not to
                if fixity:
                    try:
                        resp = self.stores['fixity'].index(file_name)
                    except Exception:
                        # It's not the end of the world if fixity indexing fails
                        self.logger.debug(
                            'Fixity indexing failed on {} for job {}'.format(
                                file_name, self.uuid))
                # Currently, do not honor generated_by passed the request
                if resp is not None:
                    self.stores['file'].add_link(
                        resp['uuid'], request.generated_by)
                indexed.add(file_name)

            indexed_list = list(indexed)
            indexed_list.sort()
            self.logger.debug('indexed {} items'.format(len(indexed_list)))
            return indexed_list

        except Exception as mexc:
            if permissive:
                return indexed
            else:
                raise IndexingError(mexc)
