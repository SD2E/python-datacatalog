.. _schema_add_defn:

Definitions
===========

Definitions are statically-defined nodes in the JSON schema. They are suited to
for constraining string values and enumerations and for defining
simple data structures comprised of Javascript primitives or other subschemas.
They are implemented in ``datacatalog.definitions``.

Add a definition
----------------
Adding a new definition requires just a few steps:

* Decide on a schema **id**. It must be unique within the SD2 namespace, between 6 and 32 characters long, contain only ``[a-z0-9_]``, and be descriptive of the schema contents.
* Create a file in ``datacatalog/definitions/jsondocs`` named after the schema id you have chosed (e.g. **<id>.json**)
* Write your schema in JSON schema Draft 7 (with 7 being preferable).
* Optional: Include examples of valid values for the schema in the ``examples`` array in the schema file
* Validate your schema using the `NewtonSoft JSON Schema Validator <https://www.jsonschemavalidator.net/>`_ or equivalent
* Ensure your schema builds and does not disrupt building of other schemas. Use **Makefile** target ``make schemas-test`` for this.
* Build a persistent instance of your new schema. Use``make schemas`` for this. Check that a schema with the appropriate name was generated and is not empty.
* Validate all built schemas. This is especially important if you have referenced other schemas from within the one you are building. Use ``make schemas-validate`` for this.
* When all is working according to plan, open a pull request to the ``python-datacatalog`` repository indicating what you have added.

Below is an example of using that Makefile target. If you see both
``SCHEMA PACKAGE`` and ``SCHEMA`` for definitions, it was likely successful.

.. code-block:: console

   $ make schemas-test
   LOCALONLY=1 MAKETESTS=1 python -m scripts.build_schemas
   ...
   SCHEMA PACKAGE definitions
   SCHEMA: definitions
   ...

Update a definition
-------------------

The workflow for updating a definition is nearly identical, save that you do
not need to create a new JSON file. Be very careful in updating existing
definitions (especially their validations and enumerations) as this can
break pipeline and data management components that depend on the project
schema if the PR including your change makes it into production.

**Measure twice. Confirm with someone else what you're going to cut. Then, cut once**
