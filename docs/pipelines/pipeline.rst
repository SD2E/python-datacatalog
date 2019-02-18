.. _pipelines_main:

=========
Pipelines
=========

In the Data Catalog, a **Pipeline** is a lexical description of specific
computational resources and static parameters that represent a data-producing
process. It is meant to be minimally expressive while conventions around
more formalized definition of pipeline are worked out. The general design of
Pipelines is that when any part changes (new value for **x**, updated version
of container **z**, etc.), the Pipeline definition changes too, yielding a new
and distinct identifier that can be used to group derived data products.

Define a Pipeline
-----------------

Pipelines are written in JSON formatted according to a specific
`JSON schema <https://schema.catalog.sd2e.org/schemas/pipeline.json>`_. Briefly,
a Pipeline has a human-readable name and description, a globally-unique string
identifier, and a list of components that defines some number of Abaco Actors,
Agave Apps, Deployed Containers, and Web Services. Additionally, one or more
data "processing levels" are provided as well as the list of file types
accepted and emitted. Of these fields, only ``components`` is used to issue the
Pipeline UUID that connects a Pipeline to various compute jobs. Below is an
extremely simple example. Others can be found in *bootstrap/pipelines*
directory of the python-datacatalog repository.

.. code: json

    {
        "name": "Jobs Demo",
        "description": "(Demo) Demonstrate integration of Reactors, Apps, and Pipelines",
        "components": [
            {
                "id": "D0ZxR0wPLpoJA",
                "image": "index.docker.io/sd2e/jobs-demo-1:latest",
                "options": {}
            }
        ],
        "processing_levels": [
            "1"
        ],
        "accepts": [
            "*"
        ],
        "produces": [
            "PLAINTEXT"
        ],
        "pipeline_type": "generic-process",
        "id": "sd2e/managedpipelinejob:101"
    }


Manage Pipelines
----------------

The management workflow is straightforward. Define a pipeline, send it as a
message to the **Pipeline Manager** Reactor or contribute it via PR to the
*bootstrap/pipelines* directory of the python-datacatalog repository. You will
receive a Pipeline UUID and an update token. The former is required for
creating jobs that reference the pipeline, and the latter is needed to update
any field besides ``components`` once the Pipeline has been created in the
*pipelines* collection in the Data Catalog.

Please see the documentation for :doc:`_reactors_pipelines_rx` for additional detail.
