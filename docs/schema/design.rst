.. _schema_design:

========
Overview
========

Data Catalog is built from a collection of linked JSON schemas, each of which
references mutliple subschemas. The entire tree of schema documents is
retrievable over the web to support active use of the schema in building
user interfaces, constructing queries, or developing extensions to the SD2
core infrastructure.

Object Schemas
--------------

- `Catalog <../challenge_problem.json>`_
- `SampleSet <../sample_set.json>`_
- `Pipeline <../pipeline.json>`_
- `PipelineJob <../pipeline_job.json>`_

Database Schemas
----------------

- `CatalogStore <../challenge_problem_document.json>`_

*Illustration*
