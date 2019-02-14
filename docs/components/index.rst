==========
Components
==========

Data Catalog is a `MongoDB <https://www.mongodb.com/>`_ database containing
multiple interlinked collections. The schema and linkage rules for those
collections is described using JSON schema and managed by code in the
``python-datcatalog`` package. Data is loaded into and managed within the
database interactively using management tools in the ``python-datcatalog``
source repository and automatically by Reactors that build on the
``python-datcatalog`` package. The Data Catalog is also populated by ETL
pipelines via interfaces to the Data Catalog.

.. toctree::
    :maxdepth: 1

    ../mongo/over
    ../schema/over
    ../python/over
    ../repo/over
    ../reactors/over
    ../pipelines/over
