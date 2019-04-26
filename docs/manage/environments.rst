=====================
Database Environments
=====================

The management scripts accept an environment flag (one of: ``-production``,
``-staging``, ``-development``, or ``-localhost``) to determine which
MongoDB connection and database to manage. These correspond to configuration
stanzas in ``config.yml`` like in the following example:

.. code: yaml

   ---
   development:
     mongodb:
       database: catalog_dev
       host: batalog.tacc.cloud
       port: 37020
       username: catalog
       password: FbgG9VR5Pgv5nTanHJ8nuPNS
       root_password: ~
   localhost:
     mongodb:
       database: catalog_local
       host: localhost
       port: 27017
       username: catalog
       password: catalog
       root_password: DNCQJGu4ZrUhMabybnG6Mx5YrGhE2EPf

To work with a specified environment environment using the management tools,
the values for the corresponding environment **must** be correct in the
``config.yml`` file.

