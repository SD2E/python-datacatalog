============
Contributing
============

The ``DataCatalog`` package is designed to be extended. It is quite tractable
for contributors not deeply familiar with the codebase or schema to extend
either.

Get the source code
-------------------

Obtain the source code and checkout the ``develop`` branch.

.. code-block:: console

    git clone https://github.com/SD2E/python-datacatalog
    cd python-datacatalog
    git checkout develop
    git pull origin develop

Unit testing
------------

All unit tests are avaiable via the Gnu Make target ``tests``

.. code-block:: console

    make tests

Several of the bundled tests exercise reading and writing from a toy instance
of MongoDB, interact with the Agave APIs, or leverage Google Drive APIs. They
are, save for the MongoDB tests, gated behind Pytest options which can be sent
to the ``make tests`` target via ``PYTEST_OPTS``. For example, here is how to
force tests that have a long run time to execute:

.. code-block:: console

    make tests PYTEST_OPTS="--longrun"

Here is an example of just running the ``jsonschemas`` tests.

.. code-block:: console

    make tests PYTEST_OPTS="-k jsonschemas"

Set up a testing MongoDB instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A MongoDB 3.6 Docker service is bundled with our tests, and is required to be
active before most tests can be run. You can stand it up using ``make`` targets
or via the ``docker-compose.yml`` file found in ``docker/``.

.. code-block:: console
   :caption: Start/stop local MongoDB

   cd python-datacatalog
   # start the service
   make mongo-up
   # shut it down
   make mongo-down

Verify that the local database server is usable in the test suite as follows:

.. code-block:: console

    make smoketest-mongo-local

Provision an TACC.cloud API client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Several functions that rely on an active TACC.cloud API client. You may need to
set one up on your development system. You can check with the following test:

.. code-block:: console

    make smoketest-agave

*Here is what to do if you need to set up a TACC.cloud client*

Set up a Google Drive service account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*To be written*

Documentation
-------------

This project uses Google-style Python documentation strings rendered via
Autodoc and the Napoleon preprocessor.

- `Google Python Style <https://google.github.io/styleguide/pyguide.html>`_
- `Example Google style docstrings <https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google>`_
- `Napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_

.. code-block:: console
   :caption: Regenerate the documentation

   make docs-clean && make docs
