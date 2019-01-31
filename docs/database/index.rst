=======
MongoDB
=======

SD2 Data Catalog is hosted on a clustered MongoDB service. The database is
directly accessible to MongoDB clients via a URL resembling the following
example. Please contact support@sd2e.org to learn the actual connection string.

``mongodb://readonly:8cWNCPXXdcxys73zBV@catalog.sd2e.org:27123/admin?readPreference=primary``

Once connected to the server, you will interact with the ``catalog`` database.

.. toctree::
   :maxdepth: 2

   shell
   pymongo
   langs
   gui
   redash
   references

.. only::  subproject and html

   Indices
   =======

   * :ref:`genindex`

