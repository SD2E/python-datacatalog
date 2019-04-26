===================
Updating the Schema
===================

The propject JSON schema is built dynamically from a combination of JSON
templates and Python package code. Detailed description of how to update the \
code and templates that generate the schema can be found elsewhere in the
documentation. The focus in this document is on regenerating and publishing
updates to the schema after your changes have passed testing.

Updating
--------

.. code-block:: console

   # Regenerate schemas
   git checkout develop
   git pull origin develop
   python -m scripts.build_schemas -localhost
   # Add schemas to git
   git add schemas
   git commit -m "Regenerated schemas from Python package"
   git checkout gh-pages
   git merge develop
   git push origin gh-pages
   git checkout develop

