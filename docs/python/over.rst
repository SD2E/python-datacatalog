.. _python_package_over:

========
Overview
========

The essential application logic, helper code, maintenance utilities, and sample
data needed to define and maintain a flexible metadata expression and
intregration framework is encapsulated in the ``DataCatalog`` package. It is
built for use in both interactive and automated manners by data
consumers data producers alike.

Key Features
------------
The Data Catalog design is based on experience with dozens of projects that
need to integrate and manage large, measured data and complex analytical
processes. Its data model includes:
   - Topics, designs, experiments, samples, and measurement artifacts
   - Reference data files
   - Analysis and ETL pipelines and jobs
   - Linkages with external resources
   - Complex types like temperature, liquid media component, and time point
   - Sophistcated parentage and derivation relationships
   - Multiple data processing levels

In addition, it is designed to be easy to extend and maintain, with declarative
representations of system behavior, a strong model of document history and
change tracking, delegated or deferred edit authority, and detailed knowledge
of record-level attribution and ownership. This is accomplished by:
   - A data model that is defined and extended using only JSON schema
   - Document that mantain creation, update, and revision history
   - Support for document- and role-level update authorizations
   - Logical isolatation of data across tenants, projects, and users

Use Cases
---------

Data Catalog code and services are used for many purposes:
   - Transform and load lab-provided metadata traces into a project Data Catalog
   - Capture and verify fixity for raw and processed data products
   - Describe and manage ETL and processing pipelines and jobs
   - Support aggregate reporting and integrity checking
   - Enable data discovery amd exploration


Where to Find It
----------------

The ``datacatalog`` package is installed in the ``sd2e/python3`` and
``sd2e/reactors:python3-edge`` Docker images. It will soon be available by
default inside the Jupyter notebooks enviroment. You can also install it
on your own local system or embed it in projects.
