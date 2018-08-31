import json
import copy
from slugify import slugify

from .mongo import db_connection, ReturnDocument, UUID_SUBTYPE
from .utils import catalog_uuid, current_time, time_stamp, validate_file_to_schema
from .dicthelpers import data_merge, dict_compare, filter_dict
from .constants import Constants, Mappings, Enumerations
from .exceptions import *
from .posixhelpers import *


class CatalogStore(object):
    def __init__(self, mongodb, config):
        self.db = db_connection(mongodb)
        coll = config['collections']['files']
        if config['debug']:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self.base = config['base']
        self.store = config['root']
        self.agave_system = config['storage_system']

    def get_fixity_properties(self, filename):
        """Safely try to learn properties of filename
        Params:
            filename (str): a datafile.filename, which is a relative path
        Returns:
            dict containing a datafiles.properties
        """
        absfilename = self.abspath(filename)
        properties = {}
        # file type
        try:
            ftype = get_filetype(absfilename)
            properties['inferred_file_type'] = ftype
        except Exception:
            pass
        # checksum
        try:
            cksum = compute_checksum(absfilename)
            properties['checksum'] = cksum
        except Exception:
            pass
        # size in bytes
        try:
            size = get_size_in_bytes(absfilename)
            properties['size_in_bytes'] = size
        except Exception:
            pass
        return properties

    def create_update_file(self, filename):
        """Create a DataFile record from a filename that resolves to a physical path
        Parameters:
            filename (str) is the filename relative to CatalogStore.root
        Returns:
            dict-like PyMongo record
        """
        # To keep the update logic simple, this is independent of the code
        # for handling records from samples.json
        filename = self.normalize(filename)
        ts = current_time()

        # Exists?
        filerec = self.coll.find_one({'filename': filename})
        newrec = False
        # Init record if not found
        if filerec is None:
            newrec = True
            filerec = {'filename': filename,
                       'uuid': catalog_uuid(filename),
                       'properties': {'created_date': ts,
                                      'modified_date': ts,
                                      'size_in_bytes': 0,
                                      'checksum': None,
                                      'revision': 0},
                       'attributes': {'lab':  lab_from_path(filename)}}

        # Update fixity
        fixity_props = self.get_fixity_properties(filename)

        # Compare fixities
        difft = False
        if 'properties' in filerec:
            for cmp in ['size_in_bytes', 'checksum', 'inferred_file_type', 'original_filename']:
                if cmp in filerec['properties'] and cmp in fixity_props:
                    if filerec['properties'].get(cmp, 0) != fixity_props.get(cmp, 0):
                        print('difft:', cmp, filerec['properties'].get(
                            cmp, None), fixity_props.get(cmp, None))
                        difft = True
                        continue

        # Merge fixity into filerec
        filerec['properties'] = data_merge(filerec['properties'], fixity_props)

        # Force thru lab attribute
        if not 'attributes' in filerec:
            filerec['attributes'] = {'lab':  lab_from_path(filename)}
            difft = True

        if newrec:
            result = self.coll.insert_one(filerec)
            return self.coll.find_one({'_id': result.inserted_id})
        else:
            try:
                if difft:
                    if 'revision' in filerec['properties']:
                        filerec['properties']['revision'] += 1
                    else:
                        filerec['properties']['revision'] = 0

                    updated = self.coll.find_one_and_replace(
                        {'uuid': filerec['uuid']},
                        filerec,
                        return_document=ReturnDocument.AFTER)
                    return updated
                else:
                    return filerec
            except Exception as exc:
                raise FileUpdateFailure('failed to write datafile', exc)

    def create_update_record(self, record):
        """Create or mod a DataFile record from a samples.json record
        Parameters:
            record (dict) is the samples.json file record
        Returns:
            dict-like PyMongo record
        """
        filename = self.normalize(record.pop('name'))
        # We need these later
        file_uuid = catalog_uuid(filename)
        ts = current_time()

        # Record with this filename exists?
        filerec = self.coll.find_one({'filename': filename})
        newrec = False
        # It does not: Create a stub record with fixity data and basic properties
        if filerec is None:
            newrec = True
            filerec = self.create_update_file(filename)
        # It does, so spot-check its fixity properties
        else:
            fixity_props = self.get_fixity_properties(filename)
            if 'properties' in filerec:
                filerec['properties'] = data_merge(
                    filerec['properties'], fixity_props)
            else:
                filerec['properties'] = fixity_props

        # Switch gears to deal with the contents of 'record'
        #
        # Transform record from samples schema into the Data Catalog
        # internal schema. 1. Lift properties and attributes, transforming
        # as needed.
        recprops = {}
        if 'size' in record:
            recprops['declared_size'] = record.pop('size')
        if 'state' in record:
            recprops['state'] = record.pop('state')
        if 'type' in record:
            recprops['declared_file_type'] = record.pop('type')
        # 2. Compute and merge fixity properties to 'record'
        fixity_props = self.get_fixity_properties(filename)
        recprops = data_merge(recprops, fixity_props)
        if 'properties' in record:
            record['properties'] = data_merge(record['properties'], recprops)
        else:
            record['properties'] = recprops
        # 3. Merge in all other top-level keys to properties
        collect_attr = {}
        for other_attr in list(record.keys()):
            if other_attr not in ('attributes', 'properties'):
                collect_attr[other_attr] = record.get(other_attr, None)
        record['attributes'] = data_merge(
            record.get('attributes', {}), collect_attr)

        # Merge 'record' onto 'filerec'
        filerec = data_merge(filerec, record)
        # Bump date and revision
        filerec['properties']['revision'] += 1
        filerec['properties']['modified_date'] = ts

        # Write the database record
        try:
            updated = self.coll.find_one_and_replace(
                {'uuid': filerec['uuid']},
                filerec,
                return_document=ReturnDocument.AFTER)
            return updated
        except Exception as exc:
            raise FileUpdateFailure('failed to write datafile', exc)

    def delete_record(self, filename):
        '''Delete record by filename'''
        filename = self.normalize(filename)
        try:
            return self.coll.remove({'filename': filename})
        except Exception:
            raise FileUpdateFailure('Delete failed')

    def query(self, query={}):
        try:
            if not isinstance(query, dict):
                query = json.loads(query)
        except Exception as exc:
            raise CatalogQueryError('query was not resolvable as dict', exc)
        try:
            return self.coll.find(query)
        except Exception as exc:
            raise CatalogQueryError('query failed')

    def normalize(self, filename):
        # Strip leading / and any combination of
        # /uploads/, /uploads, uploads/ since we
        # do not want to reference it
        if filename.startswith('/'):
            filename = filename[1:]
        if filename.startswith(self.store):
            filename = filename[len(self.store):]
        return filename

    def abspath(self, filename):
        if filename.startswith('/'):
            filename = filename[1:]
        if filename.startswith(self.store):
            filename = filename[len(self.store):]
        return os.path.join(self.base, self.store, filename)

    def checkfile(self, filepath):
        '''Check if a filepath exists and is believed by the OS to be a file'''
        full_path = self.abspath(filepath)
        return os.path.isfile(full_path)

    def to_agave_uri(self, filename):
        full_path = os.path.join(self.store, filename)
        return 'agave://' + self.agave_system + '/' + full_path


def lab_from_path(filename):
    '''Infer experimental lab from a normalized upload path'''
    if filename.startswith('/'):
        raise CatalogDataError('"{}" is not a normalized path')
    path_els = splitall(filename)
    if path_els[0].lower() in Enumerations.LABPATHS:
        return path_els[0].lower()
    else:
        raise CatalogDataError(
            '"{}" is not a known uploads path'.format(path_els[0]))

def labname_from_path(filename):
    '''Infer experimental lab from a normalized upload path'''
    if filename.startswith('/'):
        raise CatalogDataError('"{}" is not a normalized path')
    path_els = splitall(filename)
    if path_els[0].lower() in Enumerations.LABPATHS:
        return Mappings.LABPATHS.get(path_els[0].lower(), 'Unknown')
    else:
        raise CatalogDataError(
            '"{}" is not a known uploads path'.format(path_els[0]))
