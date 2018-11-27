==================
Connect to MongoDB
==================

SD2 Data Catalog is hosted on a clustered MongoDB service. The database is
directly accessible to MongoDB clients via a URL resembling the following
example. Please contact support@sd2e.org to learn the actual connection string.

``mongodb://readonly:8cWNCPXXdcxys73zBV@catalog.sd2e.org:27123/admin?readPreference=primary``

Once connected to the server, you will attach to the ``catalog`` database.

Mongo Shell
-----------

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

GUI Client
----------

These clients offer powerfule, but more accessible, access to MongoDB.

- `NoSQL Booster <https://nosqlbooster.com/download/>`_
- `Studio 3T <https://studio3t.com/download/>`_
- `MongoDB Compass <https://www.mongodb.com/products/compass>`_

Language Libraries
------------------

There are several official language-specific MongoDB drivers including:

- `C++ <http://mongocxx.org/?jmp=docs>`_
- `Java <http://mongodb.github.io/mongo-java-driver/?jmp=docs>`_
- `Node.js <https://mongodb.github.io/node-mongodb-native/?jmp=docs>`_
- `Python <https://docs.mongodb.com/ecosystem/drivers/python/>`_
- `Ruby <https://docs.mongodb.com/ruby-driver/current/>`_

.. note:: The Python driver is in-depth :doc:`elsewhere <../pymongo/index>`.

You can use MongoDB natively from other languages (though it's not supported):

- `Matlab <https://github.com/gerald-lindsly/mongo-matlab-driver>`_
- `Rstats <https://cran.r-project.org/web/packages/mongolite/>`_
- `Swift <https://github.com/OpenKitten/MongoKitten>`_

More on MongoDB
---------------

You can learn much more about working directly with MongoDB at:

- `Getting Started <https://docs.mongodb.com/manual/tutorial/getting-started/>`_
- `Mongo Shell Reference <https://docs.mongodb.com/manual/reference/method/>`_
- `Studio3T MongoDB Tutorials <https://studio3t.com/knowledge-base/categories/mongodb-tutorials/>`_

.. only::  subproject and html

   Indices
   =======

   * :ref:`genindex`
