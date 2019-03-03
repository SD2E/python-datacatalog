import os
import sys
import inspect
import json

from pprint import pprint
from slugify import slugify

from ...jsonschemas import JSONSchemaBaseObject, camel_to_snake
from ...jsonschemas import formatChecker, DateTimeEncoder
from ...identifiers import typeduuid
from ...utils import time_stamp, current_time, msec_precision

class DocumentSchema(JSONSchemaBaseObject):
    """Extends the JSON schema-driven document class with LinkedStore functions

    DocumentSchema objects validate against the schema defined in
    `schema.json`, have a defined LinkedStore type and specify fields used to
    uniquely identify the document. Their `get_schemas` method can to emit both
    document (which contains all administrative fields) and object schema (only
    core data fields).

    Attributes
        _filters (list): A private attribute defining how to render document and object schemas from the larger JSON schema

    """
    TYPED_UUID_TYPE = 'generic'
    """The named type for UUIDs assigned to this class of LinkedStore documents"""
    TYPED_UUID_FIELD = ['id']
    """List of fields used to generate a typed UUID"""
    DEFAULT_DOCUMENT_NAME = 'schema.json'
    """Filename of the JSON schema document, relative to __file__."""
    DEFAULT_FILTERS_NAME = 'filters.json'
    """Filename of the JSON schema filters document, relative to __file__."""
    RETURN_DOC_FILTERS = ['_id', '_salt', '_admin', '_properties', '_visible', '_update_token']
    """These keys should never be returned in a document"""

    def __init__(self, **kwargs):
        doc_file = kwargs.get('document', self.DEFAULT_DOCUMENT_NAME)
        filt_file = kwargs.get('filters', self.DEFAULT_FILTERS_NAME)
        modfile = inspect.getfile(self.__class__)
        try:
            # Get default schema and filter documents from this base class
            class_schemafile = os.path.join(os.path.dirname(__file__), self.DEFAULT_DOCUMENT_NAME)
            class_filtersfile = os.path.join(os.path.dirname(__file__), self.DEFAULT_FILTERS_NAME)

            # Get instance schema and filter documents
            schemafile = os.path.join(os.path.dirname(modfile), doc_file)
            filtersfile = os.path.join(os.path.dirname(modfile), filt_file)

            if os.path.isfile(schemafile):
                schemaj = json.load(open(schemafile, 'r'))
            else:
                schemaj = json.load(open(class_schemafile, 'r'))

            if os.path.isfile(filtersfile):
                filtersj = json.load(open(filtersfile, 'r'))
            elif os.path.isfile(class_filtersfile):
                filtersj = json.load(open(class_filtersfile, 'r'))
            else:
                filtersj = dict()

            setattr(self, '_filters', filtersj)
        except Exception:
            schemaj = dict()

        params = {**schemaj, **kwargs}
        super(DocumentSchema, self).__init__(**params)
        # print(self.get_collection())
        self.update_id()

    def to_dict(self, private_prefix='_', document=False, **kwargs):
        """Render LinkedStore object as a dict suitable for serialization

        Args:
            private_prefix (str): Key prefix used exclude keys from included in the dict
            document (bool): Whether to generate a document- or object-type dict

        Returns:
            dict: A dictionary containing fields represented in the document's JSON schema
        """

        schema_class = 'document' if document is True else 'object'
        response_dict = dict()
        self.update_id(document)

        filters = getattr(self, '_filters', {})
        properties_to_filter = filters.get(schema_class, {}).get('properties', [])

        # Fetch the parent schema dictionary
        # FIXME - check that this does not return values in parent dict
        super_dict = super(DocumentSchema, self).to_dict(private_prefix, **kwargs)

        # The filters.json definition doesn't support any kind of discovery
        # One can only filter a document's 'properties' by top-level key
        for key, val in super_dict.items():

            # Filter named properties from the schema
            if key == 'properties':
                filtered_props = dict()
                for fkey, fval in val.items():
                    if fkey not in properties_to_filter:
                        filtered_props[fkey] = fval
                val = filtered_props
            elif key == 'required':
                filtered_reqs = list()
                for lval in val:
                    if lval not in properties_to_filter:
                        filtered_reqs.append(lval)
                val = filtered_reqs

            response_dict[key] = val

        return response_dict

    def get_filename(self, document=False):
        """Returns basename for the schema file

        When a LinkedStore's schema is rendered, its relationship with other
        datacatalog-managed schemas is established via a common base URL. The
        basename of the URI that is embedded in the ``$id`` field of the schema
        is defined in ``__filename`` in the extended JSON schema document and
        is returned by this method.

        Returns:
            str: The filename at which this schema is expected to be resolvable
        """
        fn = getattr(self, '_filename', 'schema')
        if document is False:
            return fn
        else:
            return fn + '_document'

    def update_id(self, document=False):
        """Update the ``id`` field in the JSON schema

        This method is used solely to let us differentiate object- from
        document-form JSON schemas by incorporating a specific string
        into the schema's ``id`` field.

        Args:
            document (bool): Whether the schema is a document schema

        Returns:
            string: The updated value for schema ``id``
        """
        temp_fname = getattr(self, '_filename')
        if self._snake_case:
            temp_fname = camel_to_snake(temp_fname)
        schema_id = self.BASEREF + temp_fname
        schema_id = schema_id.lower()
        if document:
            schema_id = schema_id + '_document'
        if not schema_id.endswith('.json'):
            schema_id = schema_id + '.json'
        setattr(self, 'id', schema_id)
        return schema_id

    def get_identifiers(self):
        """Returns the list of top-level keys that are identifiers

        In the extended-form schema, ``__identifiers`` describes which keys
        can be used to uniquely identify documents written using this schema:

        Returns:
            list: The list of identifying key names

        """
        return getattr(self, '_identifiers', [])

    def get_indexes(self):
        """Returns the list of indexes declared for documents of this schema

        In the extended-form schema, ``__indexes`` declare the indexing strategy
        for documents written using this schema.

        Returns:
            list: The list of indexes declared for this schema

        """
        return getattr(self, '_indexes', [])

    def get_required(self):
        """Returns the list of required fields

        This is defined by ``__required`` in extended-form schema.

        Returns:
            list: The list of indexes declared for this schema

        """
        return getattr(self, 'required', [])

    def get_collection(self):
        """Returns the name of the MongoDB containing documents with this schema

        Documents from a LinkedStore are stored in a specific named MongoDB
        collection. This method returns the collection name. It is good
        practive for the collection and name of the LinkedStore-derived class
        to be related intuitively.

        Returns:
            str: The name of a MongoDB collection
        """
        return getattr(self, '_collection', self.COLLECTION)

    def get_uuid_type(self):
        """Returns the TypedUUID name for documents with this schema

        Each document is assigned a UUID which is a hash of values of specific
        named keys in the document. The UUID is typed with a prefix to indicate
        which kind of object it is. All LinkedStore documents have typed UUIDs,
        but there are several other types as well.

        Returns:
            str: One of the list of UUID types known to the datacatalog library
        """
        return getattr(self, '_uuid_type', self.TYPED_UUID_TYPE)

    def get_uuid_fields(self):
        """Returns the key names used to generate the document's TypedUUID

        Returns:
            list: A list of key names found in the document that contribute to its UUID
        """
        return getattr(self, '_uuid_fields', self.TYPED_UUID_FIELD)

    def get_typeduuid(self, payload, binary=False):
        """Generate a UUID with the appropriate type prefix

        Args:
            payload (str/dict): If ``payload`` is string, the UUID is generated
            directly from it. Otherwise, it is serialized before being used to
            generate the UUID.
            binary (bool, optional): Whether to return a Binary-encoded UUID.
            Defaults to `False`.

        Returns:
            str: A string validating as UUID5 with a 3-character typing prefix
        """
        # print('TYPED_UUID_PAYLOAD: {}'.format(payload))
        if isinstance(payload, dict):
            identifier_string = self.get_serialized_document(payload)
        else:
            identifier_string = str(payload)
        new_uuid = typeduuid.catalog_uuid(identifier_string, uuid_type=self.get_uuid_type(), binary=binary)
        # print('TYPED_UUID: {}'.format(new_uuid))
        return new_uuid

    def get_serialized_document(self, document, **kwargs):
        """Serializes a complex object into a string

        Some UUIDs are constructed from complex data structures like Agave job
        definitions. Rather than implement specific strategies for selecting
        from arbitrary nested structures, this method provides guaranteed-
        order serialization of the object to a linear string.

        Args:
            document (object): A dict or list object to serialize

        Returns:
            str: JSON serialized and minified representation of ``document``
        """
        # Serialize values of specific keys to generate a UUID
        union = {**document, **kwargs}
        uuid_fields = self.get_uuid_fields()
        serialized = dict()
        for k in union:
            if k in uuid_fields:
                # print('TYPED_UUID_KEY: {}'.format(k))
                serialized[k] = union.get(k)
        serialized_document = json.dumps(serialized, indent=0, sort_keys=True,
                                         separators=(',', ':'))
        return serialized_document

    def filter_keys(self):
        defined_filters = self._filters.get('object', {}).get('properties', [])
        return list(set(defined_filters + self.RETURN_DOC_FILTERS))

    @classmethod
    def time_stamp(cls):
        """Get a UTC time stamp rounded to millisecond precision

        Returns:
            object: datetime.datetime representation of utc_now()
        """
        return msec_precision(time_stamp())
