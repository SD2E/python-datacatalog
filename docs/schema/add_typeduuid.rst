.. _schema_add_typeduuid:

==========
Typed UUID
==========

Add a new typed UUID
--------------------

1. Decide on a URL-safe text identifier for the UUID. Ideally, there will be a mapping between this name and the MongoDB collection it refers to. 
2. Choose unique, non-redundant three digit identifier for UUIDs of this type
3. Write a short, descriptive description of what the identifier refers to
4. Add a tuple to the `UUIDTYPES` list in `datacatalog/identifiers/typeduuid/uuidtypes.py`
5. Add a test case to `tests/test_011_identifiers.py` in `test_validate_uuid5` and `test_get_uuidtype`
6. Rebuild and push the project JSONschema to include the new identifier.

You can now use the new UUID type across the entire Data Catalog package and managed database
