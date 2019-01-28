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


Object Schemas
--------------

- `Catalog <{{ project_schema_base_url }}/challenge_problem.json>`_
- `SampleSet <{{ project_schema_base_url }}/sample_set.json>`_
- `Pipeline <{{ project_schema_base_url }}/pipeline.json>`_
- `PipelineJob <{{ project_schema_base_url }}/pipelinejob.json>`_

Database Schemas
----------------

- `CatalogStore <{{ project_schema_base_url }}/challenge_problem_document.json>`_

*Illustration*
