===========
LinkedStore
===========

A LinkedStore manages one specififc MongoDB document collection that stores a
class of metadata record such as files or experiments. Their document schema,
linkage rules, and MongoDB indexing strategy are defined by JSON schema files
``document.json`` and ``filters.json``. The LinkedStore class also features
functions to manage linkage, issue and validate document management credentials,
and regenerate a publicly-usable instance of its own JSON schema.

Documentation
-------------
For details, please consult the :doc:`datacatalog.linkedstores <../../source/datacatalog.linkedstores>` API documentation.
