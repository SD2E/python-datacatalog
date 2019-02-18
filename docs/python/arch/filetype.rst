=========
Filetypes
=========

The ``filetypes`` module is a unified interface for classifying files by type, and
is also responsible for managing production of the ``filetype_label`` sub-
schema used to constrain file types to a known universe. It can infer file type
by a combination of filename regular expression match, Linux magic fingerprint,
and MIME-type detection using the FreeDesktop.org MIME type catalog.

Extending Filetype
------------------
It is possible to extend this module with new types by adding new members to
``filetypes/rules.py`` or by adding new entries to the system MIME-type library.

Documentation
-------------
For details, please consult the :doc:`datacatalog.filetypes <../../source/datacatalog.filetypes>` API documentation.
