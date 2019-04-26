=====
Views
=====

The ``views`` module presents a rationalized way to discover virtual document
collections implemented as MongoDB views. Each view has at least one
JSONschema, discoverable by ``get_schemas`` and a MongoDB pipeline definition,
which is available at ``get_aggregator``.  The top-level ``views`` module
supports dynamic discovery of new view schemas and aggregators. This is used to
programmatically manage the views, generate a namespaced JSON schema
representing the contents of the view, and validate that the schema and view
definitions are in alignment.

Examples
--------

.. literalinclude:: ../../../datacatalog/views/jobs_view/schema.json
   :language: python
   :linenos:
   :caption: JSON schema template

.. literalinclude:: ../../../datacatalog/views/jobs_view/aggregation.json
   :language: python
   :linenos:
   :caption: MongoDB pipeline definition

Documentation
-------------
For details, please consult the :doc:`datacatalog.views <../../source/datacatalog.views>` API documentation.
