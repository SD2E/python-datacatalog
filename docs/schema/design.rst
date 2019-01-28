.. _schema_design:

========
Overview
========

Data Catalog is built from a hiearchical tree of collection of linked JSON
schemas, accessible from the following base URL:

- **{{ project_schema_base_url }}**

Documents in this tree are accessible over HTTP so they may be imported
dynamically by code that implements user interfaces, builds database queries,
or otherwise needs to interoperate with SD2 data management infrastructure.

An index of all schema documents is maintained at:

- `Schemas <{{ project_schema_base_url }}/schemas.html>`_

Schema Forms
------------

There are two forms of presentation for the Data Catalog schema. The most
intuitive are the "object" schemas, which represent the metadata hierarchy
as a set of subdocuments. In other words, a ``sample`` document will actually
have a ``measurements`` field and that would consist of a set of measurements.

This is not how the Data Catalog is actually implemented, as the documents
would get very complex to search and work with. Instead, there are a set of
**collection** in the MongoDB database, which are linked together by
**linkage fields**, which contain the UUID of the linked object. These
relationships are discoverable by exploring the "document" schema.

Object Schemas
^^^^^^^^^^^^^^

- `Catalog <{{ project_schema_base_url }}/challenge_problem.json>`_
- `SampleSet <{{ project_schema_base_url }}/sample_set.json>`_
- `Pipeline <{{ project_schema_base_url }}/pipeline.json>`_
- `PipelineJob <{{ project_schema_base_url }}/pipelinejob.json>`_

Documement Schemas
^^^^^^^^^^^^^^^^^^

- `CatalogStore <{{ project_schema_base_url }}/challenge_problem_document.json>`_
- `PipelineJobStore <{{ project_schema_base_url }}/pipelinejob_document.json>`_

Schema Browsers
---------------

An interactive browser is available for exploring the database schema. Here
are three entrypoints as a starting point.

- `Catalog <https://browser.catalog.sd2e.org/challenge_problem.html>`_
- `SampleSet <https://browser.catalog.sd2e.org/sample_set.html>`_
- `PipelineJobStore <https://browser.catalog.sd2e.org/pipeline_job.html>`_

