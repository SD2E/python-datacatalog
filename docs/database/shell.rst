.. _connect_mongo_shell:

=========================
Connect using Mongo Shell
=========================

The ``mongo`` shell is an interactive JavaScript interface to MongoDB. You can
use it to query and update data as well as perform administrative operations.

Install MongoDB
---------------

A MongoDB installation includes both a server, which you don't need, and the
``mongo`` command line client. The client needs to be installed and available
in your ``$PATH``. You can accomplish this by following these instructions:

- `Install MongoDB Community Edition <https://docs.mongodb.com/manual/administration/install-community/>`_

.. note::  Stop after the installation steps, as you don't need to run a local MongoDB server.

Use a Docker container
----------------------

You can also leverage the Docker ecosystem:

.. code-block:: console

    # pull the container image
    docker pull mongo:3.6

    # get an interactive shell
    docker run -it mongo:3.6 bash

    # launch mongo
    root@f325a9161ad9:/# mongo
    MongoDB shell version v3.6.9
    connecting to: mongodb://127.0.0.1:27017
    ...
    exception: connect failed
    root@f325a9161ad9

.. note::  The connection error above is normal since no connection details were provided and the container is not running a MongoDB server.

Connect to the database
-----------------------

Here is a mock session that illustrates connecting to the Data Catalog and
listing the available collections.

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
