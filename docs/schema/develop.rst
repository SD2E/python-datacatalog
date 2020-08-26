.. _schema_develop:

=====================
Developing the Schema
=====================

The project metadata schema is maintained with a combination of JSON Schema
files that are referenced by the classes and methods of the ``datacatalog``
package which implement linkage and management workflow. Many nodes in the
schema are defined by static files, but some are built dynamically using
web service queries or other external sources of truth. Furthermore, the
rendered schema documents are stamped with date and current git commit and
validated against all versions of the JSON schema specification.

Consequently, extending the project schema requires a bit of Python
development experience in order to safely contribute to this shared and
project-critical resource. It is advisable to become familiar with the Python
package :doc:`architecture overview <../python/packages>` and guidance on
how to :doc:`contribute <../python/develop>` to it.

The major classes in the Python package that are extensible via editing their
JSON schema are listed here in order of increasing technical complexity.

.. toctree::
   :maxdepth: 1

   add_definition
   add_filetype
   add_identifier
   add_composition
   add_view
   add_linkedstore
   add_typeduuid
