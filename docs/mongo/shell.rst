.. _connect_mongo_shell:

===========
Mongo Shell
===========

The ``mongo`` shell is an interactive JavaScript interface to MongoDB. You can
use it to query and update data as well as perform administrative operations if
your credentials are authorized to do so.

Installing Mongo Shell
----------------------

The standard MongoDB installation includes both the server (which you don't
need), and the ``mongo`` command line client. It is difficult to get just the
client, so it is advised that you simply install MongoDB in your work
environment as per the document `Install MongoDB Community Edition <https://docs.mongodb.com/manual/administration/install-community/>`_.

Connect to the Database
-----------------------

Here is an example session that illustrates connecting to the Data Catalog and
listing the available collections. Note that the connection URI provided
here is a mock value. Request the correct value from ``support at sd2e.org``.

.. code-block:: console

    mongo mongodb://readonly:8cWNCPXXdcxys73zBV@catalog.sd2e.org:27123/admin?readPreference=primary
    MongoDB shell version v3.6.8
    connecting to: mongodb://catalog.sd2e.org:27123/admin?readPreference=primary
    MongoDB server version: 3.6.8
    rs0:PRIMARY> use catalog
    switched to db catalog
    rs0:PRIMARY> db.getCollectionNames()
    [
        "annotations",
        "challenges",
        "datafiles",
        "experiment_designs",
        "experiments",
        "files",
        "jobs",
        "measurements",
        "pipelines",
        "processes",
        "references",
        "samples",
        "science_table",
        "science_view",
        "updates"
    ]
    rs0:PRIMARY>

Use Mongo Shell from a  Docker container
-----------------------------------------

If you don't want to  or can't install MongoDB locally, a Docker container
might be the right path for you. Here's an example of how to do that.

.. code-block:: console

    # pull the container image
    docker pull mongo:latest

    # get an interactive shell
    docker run -it mongo:latest bash

    # launch mongo
    root@f325a9161ad9:/# mongo mongodb://readonly:8cWNCPXXdcxys73zBV@catalog.sd2e.org:27123/admin?readPreference=primary
    MongoDB shell version v3.6.9
    connecting to: mongodb://catalog.sd2e.org:27123/admin?readPreference=primary
    ...
    root@f325a9161ad9
