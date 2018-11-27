.. _pymongo:

=============
Using PyMongo
=============

The PyMongo package presents a Pythonic interface for connecting to, querying,
and generally manipulating information in the Data Catalog. One can interact
with individual collections or make use of **MongoDB views** such as the
``science_table``, which flatten the Data Catalog schema into a tabular (but
less expressive) format. Here's an example of connecting with PyMongo and
iterating over the results from a query against ``science_table``.

.. code-block:: python

    import pymongo
    import pprint

    dbURI = 'mongodb://readonly:8cWNCPXXdcxys73zBV@catalog.sd2e.org:27123/admin?readPreference=primary'
    client = pymongo.MongoClient(dbURI)
    db = client.catalog
    science_table=db.science_table
    query={}
    query['filename']='/uploads/biofab/201809/17987/op_92240/143184-C04.fcs'
    for match in science_table.find(query):
        pprint.pprint(match)

.. only::  subproject and html

   Indices
   =======

   * :ref:`genindex`


