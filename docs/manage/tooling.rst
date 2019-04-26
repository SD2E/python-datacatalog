==================
Management Tooling
==================

There are several tools for managing and bootstrapping the database,
collections, records, and views in the ``bootstrap`` and ``scripts``
directories. Several common workflows are available as Makefile targets.

Scripts
-------

Export Collection
#################

This script exports serialized, sanitized contents of a Data Catalog
collection to a JSON file. The contents can be edited and reloaded or used to
bootstrap loading a fresh instance of the catalog database. At present, the
entire collection is exported, but a future release will support at least
some degree of filtering.

.. code-block:: console

   usage: export_collection.py [-h] [-v] [-o OUTPUT] [-production] [-staging]
                               [-development] [-localhost]
                               {challenge_problem,experiment_design,experiment,measurement,sample,reference}

Fetch Token
###########

*Coming soon*

Fetch Admin Token
#################

*Coming soon*

Validate JSON
#############

This script can validate a JSON document either to a local or network-
accesible JSON schema. It is able to resolve schema references in order to
support complex or composed schemas.

*Usage information is coming soon*

Bootstrap Utils
----------------

Makefile Targets
----------------
