===========
JSON Schema
===========

The contents of ``schemas/`` are over 100 JSON schema files that knit together
via the JSONschema ``$ref`` mechanism to form a unified project schema. The
structure and features of that schema are described :doc: `elsewhere <../schema/index>`.

Contents of the ``schemas/`` directory are generated automatically by the
``make schemas`` build target. They are published out to
*schemas.catalog.sd2e.org* via an automated process that runs whenever a
commit is pushed to the ``gh-pages`` branch of the repository.

.. only::  subproject and html

   Indices
   =======

   * :ref:`genindex`

