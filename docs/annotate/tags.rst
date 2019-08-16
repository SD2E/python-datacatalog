====
Tags
====

Tags are 2-64 alphanumeric (plus select delimiters) characters. They have an
optional description, but it should never convey essential information, only
context for understanding the tag name. They can be associated with **ANY**
record in the Data Catalog save for other annotations, and a tag can be
associated with more than record. Tags are owned by the TACC.cloud user
who creates them, but can be published to a public context via an
administrative process.

Discover tags
-------------

You can use the ``pyython-datacatalog`` package or the CLI to explore tags and
their relationships.

.. code-block:: python
   :caption: Using python-datacatalog

    mgr = datacatalog.managers.annotation.AnnotationManager(mongodb, agave)
    mgr.list_tags(limit=-1, skip=0, only_public=True)

.. code-block:: console
   :caption: Using dcat

    dcat tags list -l LIMIT -k SKIP --only_public

Discover records associated with tags:
--------------------------------------

*Coming soon*

Create a tag
------------

Given access to production database credentials, it is possible to create
a new tag directly using the ``AnnotationManager`` class.

.. code-block:: python

    mgr = datacatalog.managers.annotation.AnnotationManager(mongodb, agave)
    mgr.create_tag(name='tag_name', description='tag_description', owner='username)

An alternative, if one has an API key that authorizes Tag management, the
CLI can be used. There will be some latency as an intermediary service is
used to create the Tag.

.. code-block:: console

    dcat tag create -t "tag_name" -d "Description"

Associate a tag with a metadata record
--------------------------------------

.. code-block:: console

    dcat association tag -t "tag_name" -u "tag_uuid" "identifier"

Remove an association
---------------------

Tag associations may be removed by the account that created them.

.. code-block:: console

    dcat association untag -t "tag_name" -u "tag_uuid" "identifier"

