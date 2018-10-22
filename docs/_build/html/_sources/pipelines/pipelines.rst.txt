=========
Pipelines
=========

Background
**********

We are able to build scalabe processing pipelines from Agave Apps and Abaco Reactors. However, the same flexibility that gives us high iteration velocity makes tracking processing job provenance quite challenging. One concern is how to definitelyt represent the collection of software entities used to do the work, and that is the scope of the Pipelines component of the Data Catalog.

Pipelines are implemented by persisent Reactor that collects and manages pipeline definitions. It is accessible by callback or direct messaging and is `(documented here) <https://gitlab.sd2e.org/sd2program/pipelines-manager>`_.

Create a Pipeline
*****************

The Pipeline JSON schema
^^^^^^^^^^^^^^^^^^^^^^^^
The current JSON schema for PipelineJob events is as follows:

.. literalinclude:: pipeline.jsonschema
   :language: json
