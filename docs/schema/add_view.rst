.. _schema_add_view:

=============
MongoDB Views
=============

The Data Catalog MongoDB features several **views**, which are read-only, live-
updated collections matching a specific query. The production views are
maintained under source control in the ``python-datacatalog`` repository.
Because the views manifest JSON documents, they are integrated with the project
schema's namespace and build system. This makes it possible to colloboratively
update the views and define the schema of their expected outputs.

Add a new view
--------------
Follow the template established by the submodules under ``datacatalog.views``.
View names are inferred from the submodule name unless specified by
``MONGODB_VIEW_NAME``. The human-readable description used in documentation is
defined by ``DESCRIPTION`` and defaults to **View on {source_collection}**. A
point-of-contact email address is specified by ``AUTHOR`` and defaults to the
Agave API tenant admin email if not specified.

.. code-block:: console
   :caption: Test using your local MongoDB installation

   $ python -m bootstrap.manage_views -localhost
   $ make bootstrap-views DB_ENV="localhost"

.. code-block:: console
   :caption: Deploy to staging (requires proper authorization)

   $ python -m bootstrap.manage_views -staging
   $ make bootstrap-views DB_ENV="staging"

.. code-block:: console
   :caption: Deploy to production (requires proper authorization)

   $ python -m bootstrap.manage_views -production
   $ make bootstrap-views DB_ENV="production"

Update a view
-------------
Edit the ``aggregation.json`` file in the view you wish to update. Test that it
works as intended by deploying your view to localhost, then staging, then
request it to be deployed on production.

Aggregations
------------

It is possible that a specific view simply cannot be computed in real time, due
to query complexity or large response size. This limitation can be mitigated by
contributing to the **datacatalog-aggregations** repository, which automates
creation and cron-scheduled maintenance of static collections
based on aggregations, but which can also include indexes.
