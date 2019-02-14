============
Architecture
============

The DataCatalog package is built from submodules implementing extensible
classes that are composed into more complex functionality. In general, module
classes inherit strongly from their superclass, are configured using
declaratively from a file or other external source, and can self-describe
as JSONschema.

.. toctree::
   :maxdepth: 1
   :caption: Key submodules

   linkedstore
   composition
   manager
   typeduuid
   filetype
   definition
   view
