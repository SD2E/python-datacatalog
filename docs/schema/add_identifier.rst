.. _schema_add_id:

===========
Identifiers
===========

Identifiers are intended to formalize representation, classification, testing,
and validation of unique identifers used by external systems and platforms.
Having this functionality embedded in ``datacatalog`` assists with data \
integration between it and data representations in other systems.  Currently,
the following identifiers are supported:

+--------------+-------------+--------------------------------------------------------------------------------------------------+-------------------------------------------+
| Platform     | Identifier  | Description                                                                                      | Module                                    |
+==============+=============+==================================================================================================+===========================================+
| Abaco        | actorId     | Identifies a distinct Abaco actor                                                                | ``datacatalog.identifiers.abaco.actorid`` |
+--------------+-------------+--------------------------------------------------------------------------------------------------+-------------------------------------------+
|              | executionId | Identifies a distinct execution of an Abaco actor                                                | ``datacatalog.identifiers.abaco.execid``  |
+--------------+-------------+--------------------------------------------------------------------------------------------------+-------------------------------------------+
|              | nonceId     | Identifies a distinct temporary API key for an Abaco actor                                       | ``datacatalog.identifiers.abaco.nonceid`` |
+--------------+-------------+--------------------------------------------------------------------------------------------------+-------------------------------------------+
|              | appId       | Identifies an Agave API app                                                                      | ``datacatalog.identifiers.agave.appid``   |
+--------------+-------------+--------------------------------------------------------------------------------------------------+-------------------------------------------+
| Agave        | UUID        | Internal, type-spaced identifier for an app, file, job, notification, metadata object, or system | ``datacatalog.identifiers.agave.uuids``   |
+--------------+-------------+--------------------------------------------------------------------------------------------------+-------------------------------------------+
| Data Catalog | typedUUID   | Internal, type-spaced identifier for any managed object in the system                            | ``datacatalog.identifiers.typeduuid``     |
+--------------+-------------+--------------------------------------------------------------------------------------------------+-------------------------------------------+

Add a new identifier type
-------------------------

Extending ``datacatalog.identifiers`` with a new type is a matter of cloning
the ``template`` directory in the ``identifiers`` directory and adapting it
to implement a new identifer. The, add unit tests, ensuring that the JSON
schema defining the new identifier(s) is generated and validates properly.

Baseline
########

Each identifier module must implement the following:

* ``generate`` - create a new ID (if possible, otherwise returns ``mock()``)
* ``get_schemas`` - return a dictionary of JSON schemas
* ``mock`` - generate or return a valid ID that does not refer to a known entity
* ``validate`` - assess whether a string represents a valid instance of the type
