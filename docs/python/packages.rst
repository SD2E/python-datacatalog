.. _python_packages:

============
Architecture
============

The DataCatalog package is built from submodules implementing extensible
classes that are composed into more complex functionality. In general, module
classes inherit strongly from their superclass, are configured using
declaratively from a file or other external source, and can self-describe
as JSONschema.

LinkedStore
-----------
A LinkedStore manages a MongoDB document collection that stores a specific kind
of metadata record, such as a file or an experiment. The schema for a specific
LinkedStore's documents is defined using a JSONschema ``document.json`` and
``filters.json`` JSON file. Each LinkedStore is expected to implement an
instance of ``HeritableDocumentSchema`` descrbing the documents to store and
``LinkedStore`` which provides document storage logic. It must also provide an
interface to report its JSONschema out when queried.

Manager
-------
Managers combine functions across multiple LinkedStores. They can be built from
basic Python objects or can inherit from ``MultiStore``. They are useful for
implementing user-facing applications atop DataCatalog.

Identifier
----------
Identifiers facilitate integration between data systems that use differing
systems of unique identifiers. Each identifier can generate mock instances
of their type and validate instances that are presented to it.

TypedUUID
^^^^^^^^^
The most important identifier is ``TypedUUID``, which is an ``uuid.UUID5``
where the initial three bytes of the UUID denote its type within the overall
DataCatalog schema. Also, a ``TypedUUID`` is not random. It is a hash of a text
string, namespaced to a specific ``UUID3`` DNS namespace. Here are a couple of
examples, for the purpose of illustration:

- ``114be7a5-d923-5039-95aa-d9d3d298061a`` defines experiment design ``YeastSTATES-gRNA-Seq-Diagnosis``
- ``10340ded-b06e-5d91-95dd-8533755ed48c`` defines sample ``sample.transcriptic.aq1bsxp36447z6``

Definition
----------
The ``definitions`` module adds named subschemas to the DataCatalog namespace.
Definitions can range from simple enumerations or formats to compositions of
JSON references. To add a new subschema, create a new JSON document in
the ``jsondocs`` directory and populate it with valid JSONschema.

Examples
^^^^^^^^

.. literalinclude:: ../../datacatalog/definitions/jsondocs/temperature_unit.json
   :language: python
   :linenos:
   :caption: temperature_unit

.. literalinclude:: ../../datacatalog/definitions/jsondocs/temperature.json
   :language: python
   :linenos:
   :caption: temperature

Composition
-----------
A composition remixes or transforms one or more DataCatalog schemas into
an alternative formulation. They are used to implement adapters or metaschemas.
Specifically, the **samples.json** schema formulation is implemented using a
composition.

Examples
^^^^^^^^

.. literalinclude:: ../../datacatalog/compositions/sample_set/document.json
   :language: python
   :linenos:
   :caption: sample_set.json

Filetype
--------

The ``filetypes`` module is a unified interface for classifying files by type, and
is also responsible for managing production of the ``filetype_label`` sub-
schema used to constrain file types to a known universe. It can infer file type
by a combination of filename regular expression match, Linux magic fingerprint,
and MIME-type detection using the FreeDesktop.org MIME type catalog. It is
extensible by adding new members to ``filetypes.rules.py`` but also by adding
new entries to the system MIME types library.

Format
------

View
----

The ``views`` module presents a rationalized way to discover virtual document
collections implemented as MongoDB views. Each view has at least one
JSONschema, discoverable by ``get_schemas`` and a MongoDB pipeline definition,
which is available at ``get_aggregator``.  The top-level ``views`` module
supports dynamic discovery of new view schemas and aggregators. This is used to
programmatically manage the views, generate a namespaced JSON schema
representing the contents of the view, and validate that the schema and view
definitions are in alignment.

Examples
^^^^^^^^

.. literalinclude:: ../../datacatalog/views/job_view/document.json
   :language: python
   :linenos:
   :caption: JSON schema template

.. literalinclude:: ../../datacatalog/views/job_view/aggregation.json
   :language: python
   :linenos:
   :caption: MongoDB pipeline definition
