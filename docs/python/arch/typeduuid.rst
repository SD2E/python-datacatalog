TypedUUID
=========

The critical type of identifier for Data Caalog is ``TypedUUID``, which is
an ``uuid.UUID5`` where the initial three bytes of the UUID denote its type
in the overall DataCatalog schema. Typed UUIDS are not, as a rule, random or
incremental values. They are usually a hash of one more more text strings that
uniquely identify a Data Catalog record, transformed with a defined ``UUID3``
DNS namespace.

Here are a couple of examples to illustrate:

- ``114be7a5-d923-5039-95aa-d9d3d298061a`` == experiment design ``YeastSTATES-gRNA-Seq-Diagnosis``
- ``10340ded-b06e-5d91-95dd-8533755ed48c`` == sample ``sample.transcriptic.aq1bsxp36447z6``

TypedUUID Types
----------------

{{ table_typeduuid_types }}

Documentation
-------------
For details, please consult the :doc:`datacatalog.identifiers.typeduuid <../../source/datacatalog.identifiers.typeduuid>` API documentation.
