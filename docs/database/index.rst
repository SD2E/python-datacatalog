================
MongoDB Database
================

SD2 Data Catalog is hosted using a clustered MongoDB service. The database is
directly accessible to MongoDB clients via a URL resembling the following
example. Please contact support@sd2e.org to learn the actual connection string.

``mongodb://readonly:8cWNCPXXdcxys73zBV@catalog.sd2e.org:27123/admin?readPreference=primary``

Once connected to the server, you will attach to the ``catalog`` database.

Connect via Mongo Shell
-----------------------

Here is a mock example of connecting to the Data Catalog and listing the
available collections.

.. code-block:: console

    mongo mongodb://readonly:8cWNCPXXdcxys73zBV@catalog.sd2e.org:27123/admin?readPreference=primary
    MongoDB shell version v3.6.8
    connecting to: mongodb://catalog.sd2e.org:27123/admin?readPreference=primary
    MongoDB server version: 3.6.8
    rs0:PRIMARY> use catalog
    switched to db catalog
    rs0:PRIMARY> db.getCollectionNames()
    [
        "agave_path",
        "challenges",
        "datafiles",
        "experiment_designs",
        "experiments",
        "files",
        "files-fixity",
        "job_view",
        "jobs",
        "measurements",
        "path_mapping",
        "pipelines",
        "samples",
        "science_table",
        "science_view",
        "system.profile",
        "system.views",
        "updates"
    ]
    rs0:PRIMARY>

GUI Clients
-----------

- `NoSQL Booster <https://nosqlbooster.com/download/>`_
- `Studio 3T <https://studio3t.com/download/>`_
- `MongoDB Compass <https://www.mongodb.com/products/compass>`_

Learn More
----------

For more guidance on working directly with MongoDB, please consult:

- `Getting Started <https://docs.mongodb.com/manual/tutorial/getting-started/>`_
- `Mongo Shell Reference <https://docs.mongodb.com/manual/reference/method/>`_
- `Studio3T MongoDB Tutorials <https://studio3t.com/knowledge-base/categories/mongodb-tutorials/>`_

.. only::  subproject and html

   Indices
   =======

   * :ref:`genindex`
