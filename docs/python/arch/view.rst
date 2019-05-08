=====
Views
=====

The ``views`` module presents a rationalized way to configure virtual
collections implemented as MongoDB views. Each view is implemented as a Python
submodule under ``datacatalog.views``, where each view is configured via a
combination of its ``__init__.py`` and ``aggregation.json`` file. The ``views``
module is leveraged by the ``bootstrap.manage_views`` script to allow an
authorized MongoDB user to update any or all views.

Current Views
-------------
{{ current_views }}

Example Configuration
---------------------

.. literalinclude:: ../../../datacatalog/views/jobs_view/__init__.py
   :language: python
   :linenos:
   :caption: init.py file

.. literalinclude:: ../../../datacatalog/views/jobs_view/aggregation.json
   :language: json
   :linenos:
   :caption: pipeline definition

Documentation
-------------
For details, please consult the :doc:`datacatalog.views <../../source/datacatalog.views>` API documentation.
