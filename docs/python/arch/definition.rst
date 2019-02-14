==========
Definition
==========

The ``definitions`` module adds named subschemas to the DataCatalog namespace.
Definitions can range from simple enumerations or formats to compositions of
JSON references.

Examples
--------

.. literalinclude:: ../../../datacatalog/definitions/jsondocs/temperature_unit.json
   :language: python
   :linenos:
   :caption: temperature_unit

.. literalinclude:: ../../../datacatalog/definitions/jsondocs/temperature.json
   :language: python
   :linenos:
   :caption: temperature

Adding a sub-schema
--------------------

To add a new subschema, create a new JSON document in the ``jsondocs``
directory and populate it with valid JSONschema. It is possible and
encouraged to link with the rest of the SD2E schema for
context and ease of validation.

Documentation
-------------
For details, please consult the :doc:`datacatalog.definitions <../../source/datacatalog.definitions>` API documentation.
